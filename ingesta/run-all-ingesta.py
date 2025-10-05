#!/usr/bin/env python3
"""
Script principal para ejecutar todas las ingestas de datos a S3
Ejecuta los scripts de MySQL, PostgreSQL y MongoDB de forma secuencial o individual
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IngestaManager:
    def __init__(self):
        self.base_path = Path(__file__).parent
        
        # Configuración de scripts
        self.scripts = {
            'mysql': {
                'path': self.base_path / 'mysql-rooms-api' / 'script-ingesta-mysql.py',
                'name': 'MySQL (Rooms API)',
                'description': 'Salas, asientos y horarios'
            },
            'postgresql': {
                'path': self.base_path / 'postgresql-reservations-api' / 'script-ingesta-postgresql.py',
                'name': 'PostgreSQL (Reservations API)',
                'description': 'Usuarios, reservas y pagos'
            },
            'mongodb': {
                'path': self.base_path / 'mongodb-movies-api' / 'script-ingesta-mongodb.py',
                'name': 'MongoDB (Movies API)',
                'description': 'Películas y géneros'
            }
        }
    
    def check_script_exists(self, script_key):
        """Verificar si existe el script"""
        script_path = self.scripts[script_key]['path']
        if not script_path.exists():
            logger.error(f"❌ Script no encontrado: {script_path}")
            return False
        return True
    
    def run_script(self, script_key, test_mode=False):
        """Ejecutar un script individual"""
        if not self.check_script_exists(script_key):
            return False
        
        script_info = self.scripts[script_key]
        script_path = script_info['path']
        
        logger.info(f"🚀 Ejecutando: {script_info['name']}")
        logger.info(f"📂 Ruta: {script_path}")
        
        try:
            # Cambiar al directorio del script
            script_dir = script_path.parent
            original_cwd = os.getcwd()
            os.chdir(script_dir)
            
            # Preparar comando
            # Preparar comando con parámetro auto si no es modo test
            if test_mode:
                cmd = [sys.executable, str(script_path.name)]
            else:
                cmd = [sys.executable, str(script_path.name), 'auto']
            
            # Ejecutar el script
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Si es modo test, enviar "1" automáticamente
            if test_mode:
                stdout, stderr = process.communicate(input="1\n")
            else:
                # Modo automático - no necesita input
                stdout, stderr = process.communicate()
            
            # Restaurar directorio original
            os.chdir(original_cwd)
            
            if process.returncode == 0:
                logger.info(f"✅ {script_info['name']} completado exitosamente")
                if stdout:
                    print(f"\n--- Output de {script_info['name']} ---")
                    print(stdout)
                return True
            else:
                logger.error(f"❌ {script_info['name']} falló con código: {process.returncode}")
                if stderr:
                    print(f"\n--- Error de {script_info['name']} ---")
                    print(stderr)
                return False
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando {script_info['name']}: {e}")
            return False
    
    def run_all_scripts(self, test_mode=False):
        """Ejecutar todos los scripts de ingesta"""
        logger.info("🚀 Iniciando ingesta completa de todas las bases de datos...")
        
        results = {}
        total_start_time = datetime.now()
        
        for script_key in ['mysql', 'postgresql', 'mongodb']:
            script_info = self.scripts[script_key]
            
            print(f"\n{'='*60}")
            print(f"🔄 Procesando: {script_info['name']}")
            print(f"📋 Datos: {script_info['description']}")
            print(f"{'='*60}")
            
            start_time = datetime.now()
            success = self.run_script(script_key, test_mode)
            end_time = datetime.now()
            
            results[script_key] = {
                'success': success,
                'duration': end_time - start_time
            }
            
            if success:
                logger.info(f"✅ {script_info['name']} - Completado en {results[script_key]['duration']}")
            else:
                logger.error(f"❌ {script_info['name']} - Falló después de {results[script_key]['duration']}")
        
        # Resumen final
        total_end_time = datetime.now()
        total_duration = total_end_time - total_start_time
        
        print(f"\n{'='*60}")
        print("📊 RESUMEN DE INGESTA")
        print(f"{'='*60}")
        
        successful = 0
        for script_key, result in results.items():
            script_name = self.scripts[script_key]['name']
            status = "✅ EXITOSO" if result['success'] else "❌ FALLIDO"
            print(f"{status:12} | {script_name:30} | {result['duration']}")
            if result['success']:
                successful += 1
        
        print(f"\n📈 Resultados: {successful}/{len(results)} scripts exitosos")
        print(f"⏱️  Tiempo total: {total_duration}")
        
        if successful == len(results):
            print("\n🎉 ¡INGESTA COMPLETA EXITOSA!")
            print("🚀 Todas las bases de datos han sido subidas a S3")
        else:
            print(f"\n⚠️  INGESTA PARCIAL: {successful} de {len(results)} completadas")
        
        return successful == len(results)
    
    def show_menu(self):
        """Mostrar menú interactivo"""
        while True:
            print(f"\n{'='*50}")
            print("🚀 SISTEMA DE INGESTA A S3 - AWS ACADEMY")
            print(f"{'='*50}")
            print("¿Qué deseas hacer?")
            print()
            print("1. 🧪 Test rápido (todas las bases de datos)")
            print("2. 📦 Ingesta completa (todas las bases de datos)")
            print("3. 🎯 Ejecutar script individual")
            print("4. ℹ️  Ver información de scripts")
            print("5. 🚪 Salir")
            print()
            
            choice = input("Elige una opción (1-5): ").strip()
            
            if choice == '1':
                print("\n🧪 Ejecutando test rápido de todas las bases de datos...")
                self.run_all_scripts(test_mode=True)
                
            elif choice == '2':
                print("\n📦 Ejecutando ingesta completa de todas las bases de datos...")
                self.run_all_scripts(test_mode=False)
                
            elif choice == '3':
                self.show_individual_menu()
                
            elif choice == '4':
                self.show_info()
                
            elif choice == '5':
                print("👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción no válida. Por favor elige 1-5.")
    
    def show_individual_menu(self):
        """Mostrar menú para scripts individuales"""
        print("\n📝 Scripts disponibles:")
        
        for i, (key, script_info) in enumerate(self.scripts.items(), 1):
            status = "✅" if self.check_script_exists(key) else "❌"
            print(f"{i}. {status} {script_info['name']}")
            print(f"   📋 {script_info['description']}")
        
        print(f"{len(self.scripts)+1}. 🔙 Volver al menú principal")
        
        choice = input(f"\nElige script (1-{len(self.scripts)+1}): ").strip()
        
        try:
            choice_num = int(choice)
            if choice_num == len(self.scripts) + 1:
                return
            elif 1 <= choice_num <= len(self.scripts):
                script_keys = list(self.scripts.keys())
                selected_key = script_keys[choice_num - 1]
                
                test_choice = input("\n¿Ejecutar en modo test? (s/N): ").strip().lower()
                test_mode = test_choice in ['s', 'si', 'yes', 'y']
                
                self.run_script(selected_key, test_mode)
            else:
                print("❌ Opción no válida")
        except ValueError:
            print("❌ Por favor ingresa un número válido")
    
    def show_info(self):
        """Mostrar información de los scripts"""
        print(f"\n{'='*50}")
        print("ℹ️  INFORMACIÓN DE SCRIPTS")
        print(f"{'='*50}")
        
        for key, script_info in self.scripts.items():
            status = "✅ Disponible" if self.check_script_exists(key) else "❌ No encontrado"
            
            print(f"\n📊 {script_info['name']}")
            print(f"   📁 Ruta: {script_info['path']}")
            print(f"   📋 Descripción: {script_info['description']}")
            print(f"   🔍 Estado: {status}")
        
        print(f"\n💡 Notas importantes:")
        print("   • Asegúrate de tener las credenciales AWS Academy configuradas")
        print("   • Verifica que las bases de datos estén ejecutándose")
        print("   • Los archivos .env deben tener las configuraciones correctas")

def main():
    """Función principal"""
    try:
        manager = IngestaManager()
        
        # Si se pasa argumento de línea de comandos
        if len(sys.argv) > 1:
            arg = sys.argv[1].lower()
            
            if arg in ['test', 't']:
                print("🧪 Modo test automático")
                manager.run_all_scripts(test_mode=True)
            elif arg in ['full', 'f']:
                print("📦 Modo ingesta completa automática")
                manager.run_all_scripts(test_mode=False)
            elif arg in manager.scripts:
                print(f"🎯 Ejecutando script individual: {arg}")
                manager.run_script(arg)
            else:
                print(f"❌ Argumento no válido: {arg}")
                print("💡 Argumentos válidos: test, full, mysql, postgresql, mongodb")
        else:
            # Modo interactivo
            manager.show_menu()
            
    except KeyboardInterrupt:
        print("\n\n🛑 Operación cancelada por el usuario")
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()