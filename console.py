import sys
import threading
from database import Database
from utils import Utils
from config import logger

class ConsoleHandler:
    @staticmethod
    def handle_console_command():
        """Обработка консольных команд"""
        try:
            command = input().strip()
            if not command:
                return
            
            parts = command.split()
            if len(parts) < 2:
                print("❌ Использование: /op @username или /unop @username")
                return
            
            action = parts[0].lower()
            username = Utils.extract_username(parts[1])
            
            if not username:
                print("❌ Неверный username!")
                return
            
            if action == "/op":
                if Database.add_operator(username):
                    print(f"✅ @{username} повышен до оператора")
                    logger.info(f"CONSOLE: @{username} повышен до оператора")
                else:
                    print(f"❌ Не удалось повысить @{username}")
            
            elif action == "/unop":
                if Database.remove_operator(username):
                    print(f"✅ @{username} понижен с оператора")
                    logger.info(f"CONSOLE: @{username} понижен с оператора")
                else:
                    print(f"❌ Не удалось понизить @{username}")
            
            else:
                print("❌ Неизвестная команда. Доступно: /op, /unop")
                
        except Exception as e:
            print(f"❌ Ошибка обработки команды: {e}")
            logger.error(f"Console command error: {e}")

    @staticmethod
    def start_console_listener():
        """Запуск прослушивания консольных команд в отдельном потоке"""
        def console_loop():
            print("\n🎮 Консольный режим активирован")
            print("Доступные команды:")
            print("  /op @username    - повысить до оператора")
            print("  /unop @username  - понизить с оператора")
            print("Для выхода: Ctrl+C\n")
            
            while True:
                try:
                    ConsoleHandler.handle_console_command()
                except KeyboardInterrupt:
                    print("\n👋 Завершение работы консоли...")
                    break
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
                    continue
        
        # Запускаем в отдельном потоке
        console_thread = threading.Thread(target=console_loop, daemon=True)
        console_thread.start()
        return console_thread