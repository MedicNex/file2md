#!/usr/bin/env python3
"""
YBU 延边大学自动选课代理系统 - 主程序入口
延边大学教务系统自动选课代理系统

使用方法：
python main.py login                    # 首次登录
python main.py list                     # 查看课程列表
python main.py plan rules.yml           # 根据规则规划选课
python main.py grab CJ000123            # 抢课
python main.py scheduler start          # 启动调度器
"""

import asyncio
import sys
import os
import platform
from pathlib import Path

# Windows 异步兼容性修复
if platform.system() == 'Windows':
    # 设置 Windows 事件循环策略
    if sys.version_info >= (3, 8):
        try:
            # 在 Windows 上使用 ProactorEventLoop 来避免异步问题
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except AttributeError:
            # 如果没有 WindowsProactorEventLoopPolicy，则使用默认策略
            pass
    
    # Python 3.11 专用修复：禁用资源警告和管道错误
    if sys.version_info >= (3, 11):
        import warnings
        warnings.filterwarnings("ignore", category=ResourceWarning, module="asyncio")
        
        # 设置环境变量禁用某些警告
        os.environ.setdefault('PYTHONWARNINGS', 'ignore::ResourceWarning')
        
        # 针对管道错误的特殊处理
        try:
            import asyncio.windows_utils
            original_fileno = asyncio.windows_utils.PipeHandle.fileno
            
            def safe_fileno(self):
                try:
                    return original_fileno(self)
                except ValueError:
                    return -1
            
            asyncio.windows_utils.PipeHandle.fileno = safe_fileno
        except (ImportError, AttributeError):
            pass
    
    # 修复Windows下的显示问题
    try:
        import colorama
        colorama.init(autoreset=True)
    except ImportError:
        pass

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents import (
    BrowserAgent,
    CaptchaSolverAgent,
    DataManagerAgent,
    SchedulerAgent,
    CLIInterfaceAgent
)


async def main():
    """主函数"""
    # 创建 CLI 代理
    cli_agent = CLIInterfaceAgent()
    
    # 显示欢迎信息
    cli_agent.display_welcome()
    
    # 解析命令行参数
    parser = cli_agent._setup_argument_parser()
    args = parser.parse_args()
    
    # 如果没有提供命令，显示帮助
    if not args.command:
        await cli_agent._show_help()
        return
    
    # 初始化各个代理
    try:
        # 创建浏览器代理
        headless_mode = cli_agent.config.get('headless', True)
        # 如果用户指定了 --headful 参数，则覆盖配置
        if hasattr(args, 'headful') and args.headful:
            headless_mode = False
        
        browser_agent = BrowserAgent(
            headless=headless_mode
        )
        
        # 创建验证码识别代理
        # 只有当配置中有 ocr_engine 时才传递给 CaptchaSolverAgent
        ocr_engine = cli_agent.config.get('ocr_engine')
        if ocr_engine:
            captcha_solver = CaptchaSolverAgent(engine=ocr_engine)
        else:
            captcha_solver = CaptchaSolverAgent()  # 使用默认构造函数
        
        # 创建数据管理代理
        data_manager = DataManagerAgent()
        
        # 创建调度代理
        scheduler = SchedulerAgent()
        
        # 注册调度器回调
        async def course_check_callback():
            """课程检查回调"""
            await browser_agent.start()
            try:
                courses_data = await browser_agent.fetch_courses()
                data_manager.save_courses(courses_data)
                
                # 检查每个课程的可用性
                for course_type, courses in courses_data.items():
                    if course_type == 'all':  # 跳过汇总列表
                        continue
                    for course in courses[:5]:  # 限制检查数量避免过载
                        availability = await browser_agent.check_course_availability(
                            course['id'], course.get('is_retake', False)
                        )
                        # 适配新的数据结构
                        old_format = {
                            'remaining': availability.get('total_remaining', 0),
                            'jx0404id': availability.get('best_class', {}).get('jx0404id', '') if availability.get('best_class') else ''
                        }
                        data_manager.save_course_availability(course['id'], old_format)
            finally:
                await browser_agent.stop()
        
        async def auto_enroll_callback(course_id: str) -> bool:
            """自动选课回调"""
            await browser_agent.start()
            try:
                # 检查课程可用性
                availability = await browser_agent.check_course_availability(
                    course_id, False  # 默认为普通选课，实际需要从数据库查询
                )
                
                if not availability['available']:
                    return False
                
                # 获取验证码
                captcha_image = await browser_agent.get_captcha_image()
                if captcha_image:
                    captcha_code = captcha_solver.solve_captcha(
                        captcha_image, manual_fallback=False
                    )
                    
                    if captcha_code:
                        success = await browser_agent.select_course(
                            course_id,
                            False  # 默认为普通选课
                        )
                        
                        # 记录结果
                        status = 'success' if success else 'failed'
                        best_jx0404id = availability.get('best_class', {}).get('jx0404id', '') if availability.get('best_class') else ''
                        data_manager.save_enrollment_record(
                            course_id, best_jx0404id, 'enroll', status
                        )
                        
                        return success
                
                return False
            finally:
                await browser_agent.stop()
        
        async def notification_callback(message: str, level: str):
            """通知回调"""
            # 这里可以扩展其他通知方式，如邮件、钉钉等
            pass
        
        # 注册回调
        scheduler.register_callback('course_check', course_check_callback)
        scheduler.register_callback('auto_enroll', auto_enroll_callback)
        scheduler.register_callback('notification', notification_callback)
        
        # 将代理实例注入到 CLI 代理
        cli_agent.set_agents(browser_agent, captcha_solver, data_manager, scheduler)
        
        # 处理命令
        await cli_agent.run()
        
    except KeyboardInterrupt:
        print("\n👋 用户中断，正在安全退出...")
    except Exception as e:
        print(f"❌ 程序执行出错：{e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
    finally:
        # 清理资源
        cli_agent.close()


if __name__ == "__main__":
    # Windows 专用异步运行机制
    if platform.system() == 'Windows':
        try:
            # 运行主程序
            asyncio.run(main())
        except SystemExit:
            pass
        except KeyboardInterrupt:
            print("\n👋 用户中断，正在安全退出...")
        except Exception as e:
            print(f"❌ 程序执行出错：{e}")
        finally:
            # 强制清理所有异步资源
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_closed():
                    # 取消所有挂起的任务
                    pending = asyncio.all_tasks(loop)
                    for task in pending:
                        task.cancel()
                    
                    # 等待任务完成或取消
                    if pending:
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    
                    # 关闭循环
                    loop.close()
            except Exception:
                pass
    else:
        # 非Windows系统使用标准运行方式
        asyncio.run(main()) 