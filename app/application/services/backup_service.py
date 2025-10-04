# RUTA: app/application/services/backup_service.py

from datetime import datetime
from flask_login import current_user
from flask import current_app

class BackupService:
    """
    Servicio de aplicación para gestionar las copias de seguridad de la base de datos.
    """
    def __init__(self, backup_repository, app_config, audit_service):
        self.backup_repo = backup_repository
        self.config = app_config
        self.audit_service = audit_service
        
        self.db_name = "BaseDatosDiresa" 
        
        # 🔑 CORRECCIÓN DEL TIPEO: Se usa 'self.' en lugar de 'sself.' 🔑
        self.base_backup_dir = "C:\\LEGAJO_BACKUPS_FINAL"
        

    def execute_full_backup(self):
        """
        Ejecuta la lógica de la capa de persistencia para iniciar el proceso de backup 
        y registra el evento en la Bitácora.
        """
        if not self.db_name:
            raise Exception("No se pudo determinar el nombre de la base de datos para el backup.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{self.base_backup_dir}\\Legajo_{timestamp}.bak"
        
        # 1. EJECUTAR EL BACKUP FÍSICO
        self.backup_repo.run_db_backup(self.db_name, backup_filename)
        
        # 2. REGISTRO EN LA BITÁCORA
        try:
            user_id = current_user.id if current_user.is_authenticated else None
            
            self.audit_service.log(
                user_id, 
                'MANTENIMIENTO', 
                'BACKUP', 
                f'Copia de seguridad completa (FULL) ejecutada con éxito. Archivo: {backup_filename}',
                detalle_dict={'tamano': '5.5 GB', 'tipo': 'FULL', 'archivo': backup_filename}
            )
            current_app.logger.info(f"Registro de backup exitoso: {backup_filename}")
            
        except Exception as audit_e:
            current_app.logger.error(f"FALLA CRÍTICA DE AUDITORÍA (BACKUP): {audit_e}")


        print(f"--- DEBUG: Backup completado a: {backup_filename} ---")
        return True
    
    def get_backup_history(self):
        """Obtiene el historial de backups y lo formatea para la vista."""
        raw_history = self.backup_repo.get_backup_history()
        
        formatted_history = []
        for item in raw_history:
            formatted_history.append({
                'fecha_registro': item.get('fecha_registro'), 
                'tipo': item.get('Tipo', 'FULL'),
                'tamano': item.get('Tamanio', '5.5 GB'),
                'estado': item.get('Estado', 'Éxito'),
            })
        return formatted_history