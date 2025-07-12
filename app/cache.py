"""
Redis缓存管理模块

提供文件解析结果的缓存功能，通过MD5 hash识别文件
"""
import hashlib
import json
import redis.asyncio as redis
from typing import Optional, Dict, Any
from loguru import logger
import time

from app.config import config


class CacheManager:
    """Redis缓存管理器"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = config.REDIS_CACHE_ENABLED
        
    async def initialize(self) -> bool:
        """
        初始化Redis连接
        
        Returns:
            是否成功初始化
        """
        if not self.enabled:
            logger.info("Redis缓存已禁用")
            return False
            
        try:
            # 创建Redis连接池
            self.redis_client = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                password=config.REDIS_PASSWORD,
                db=config.REDIS_DB,
                socket_connect_timeout=config.REDIS_CONNECTION_TIMEOUT,
                socket_timeout=config.REDIS_CONNECTION_TIMEOUT,
                max_connections=config.REDIS_MAX_CONNECTIONS,
                decode_responses=True
            )
            
            # 测试连接
            await self.redis_client.ping()
            logger.info(f"Redis缓存已启用，连接到 {config.REDIS_HOST}:{config.REDIS_PORT}")
            return True
            
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            self.redis_client = None
            self.enabled = False
            return False
    
    async def close(self):
        """关闭Redis连接"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis连接已关闭")
    
    def calculate_file_hash(self, file_content: bytes) -> str:
        """
        计算文件内容的MD5哈希值
        
        Args:
            file_content: 文件内容字节
            
        Returns:
            MD5哈希字符串
        """
        # 对于大文件，使用流式处理减少内存压力
        if len(file_content) > 50 * 1024 * 1024:  # 50MB以上使用流式处理
            hash_md5 = hashlib.md5()
            chunk_size = 64 * 1024  # 64KB块
            for i in range(0, len(file_content), chunk_size):
                chunk = file_content[i:i + chunk_size]
                hash_md5.update(chunk)
            return hash_md5.hexdigest()
        else:
            return hashlib.md5(file_content).hexdigest()
    
    def _get_cache_key(self, file_hash: str) -> str:
        """
        生成缓存键
        
        Args:
            file_hash: 文件MD5哈希
            
        Returns:
            Redis缓存键
        """
        return f"file2md:cache:{file_hash}"
    
    async def get_cached_result(self, file_content: bytes) -> Optional[Dict[str, Any]]:
        """
        从缓存获取解析结果
        
        Args:
            file_content: 文件内容字节
            
        Returns:
            缓存的解析结果，如果不存在则返回None
        """
        if not self.enabled or not self.redis_client:
            return None
            
        try:
            file_hash = self.calculate_file_hash(file_content)
            cache_key = self._get_cache_key(file_hash)
            
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                result = json.loads(cached_data)
                result['from_cache'] = True
                result['cache_hit_time'] = int(time.time() * 1000)
                
                logger.info(f"缓存命中: {file_hash[:8]}...")
                return result
            
            logger.debug(f"缓存未命中: {file_hash[:8]}...")
            return None
            
        except Exception as e:
            logger.error(f"读取缓存失败: {e}")
            return None
    
    async def cache_result(self, file_content: bytes, filename: str, markdown_content: str, 
                          file_size: int, duration_ms: int, content_type: str | None = None) -> bool:
        """
        缓存解析结果
        
        Args:
            file_content: 文件内容字节
            filename: 文件名
            markdown_content: 解析后的Markdown内容
            file_size: 文件大小
            duration_ms: 解析耗时（毫秒）
            content_type: 文件类型
            
        Returns:
            是否成功缓存
        """
        if not self.enabled or not self.redis_client:
            return False
            
        try:
            file_hash = self.calculate_file_hash(file_content)
            cache_key = self._get_cache_key(file_hash)
            
            cache_data = {
                'filename': filename,
                'content': markdown_content,
                'size': file_size,
                'content_type': content_type or 'application/octet-stream',
                'duration_ms': duration_ms,
                'cached_time': int(time.time() * 1000),
                'file_hash': file_hash
            }
            
            # 缓存数据，设置TTL
            await self.redis_client.setex(
                cache_key,
                config.REDIS_CACHE_TTL,
                json.dumps(cache_data, ensure_ascii=False)
            )
            
            logger.info(f"缓存已保存: {file_hash[:8]}... -> {filename}")
            return True
            
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")
            return False
    
    async def clear_cache(self, pattern: str = "file2md:cache:*") -> int:
        """
        清除匹配模式的缓存
        
        Args:
            pattern: 缓存键模式
            
        Returns:
            清除的缓存条目数量
        """
        if not self.enabled or not self.redis_client:
            return 0
            
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(f"清除了 {deleted} 条缓存记录")
                return deleted
            return 0
            
        except Exception as e:
            logger.error(f"清除缓存失败: {e}")
            return 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计数据
        """
        if not self.enabled or not self.redis_client:
            return {"enabled": False}
            
        try:
            # 获取匹配的键数量
            keys = await self.redis_client.keys("file2md:cache:*")
            cache_count = len(keys)
            
            # 获取Redis信息
            info = await self.redis_client.info()
            
            return {
                "enabled": True,
                "cache_count": cache_count,
                "redis_version": info.get("redis_version"),
                "used_memory_human": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "cache_ttl_hours": config.REDIS_CACHE_TTL // 3600
            }
            
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {"enabled": True, "error": str(e)}


# 全局缓存管理器实例
cache_manager = CacheManager()


async def init_cache():
    """初始化缓存管理器"""
    await cache_manager.initialize()


async def close_cache():
    """关闭缓存管理器"""
    await cache_manager.close() 