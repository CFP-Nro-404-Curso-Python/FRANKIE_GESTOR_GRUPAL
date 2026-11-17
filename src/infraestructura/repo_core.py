"""
===============================================================================
MÓDULO DE INFRAESTRUCTURA: REPOSITORIO CORE (src/infraestructura/repo_core.py)
===============================================================================
Gestiona la persistencia de usuarios, verificación de contraseñas y asignación
de roles para la autenticación segura en el sistema, adaptado al esquema oficial.
===============================================================================
"""

import hashlib
from typing import Optional
from infraestructura.conexion import ConexionDB
from dominio.entidades_core import Usuario, Rol


class RepoCore:
    """
    Repositorio encargado de las operaciones de autenticación, consulta de usuarios
    y mapeo de roles de seguridad.
    """

    @staticmethod
    def _hashear_password(password: str) -> str:
        """Genera un hash seguro para la contraseña utilizando SHA-256."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @classmethod
    def autenticar_usuario(cls, username: str, password_plana: str) -> Optional[Usuario]:
        """
        Valida las credenciales de acceso de un usuario en la base de datos.
        Retorna el objeto Usuario con sus roles si las credenciales son correctas, o None en caso contrario.
        """
        with ConexionDB() as conn:
            cursor = conn.cursor()

            # 1. Buscar el usuario activo consultando la columna 'password' del esquema oficial
            cursor.execute(
                """
                SELECT id, username, password, activo
                FROM usuarios
                WHERE username = ? AND activo = 1;
                """,
                (username,)
            )
            row = cursor.fetchone()
            if not row:
                return None

            # 2. Verificar contraseña (soporte tanto para hash SHA-256 como texto plano por defecto)
            password_hash_calculado = cls._hashear_password(password_plana)
            password_almacenada = row["password"]

            if password_almacenada != password_hash_calculado and password_almacenada != password_plana:
                return None

            id_usuario = row["id"]
            usuario = Usuario(
                id_usuario=id_usuario,
                username=row["username"],
                password_hash=password_almacenada,
                activo=row["activo"]
            )

            # 3. Cargar roles asociados usando la tabla intermedia oficial 'usuarios_roles'
            cursor.execute(
                """
                SELECT r.id, r.nombre, r.descripcion
                FROM roles r
                JOIN usuarios_roles ur ON r.id = ur.id_rol
                WHERE ur.id_usuario = ?;
                """,
                (id_usuario,)
            )
            filas_roles = cursor.fetchall()
            for r_row in filas_roles:
                rol = Rol(
                    id_rol=r_row["id"],
                    nombre=r_row["nombre"],
                    descripcion=r_row["descripcion"] or ""
                )
                usuario.agregar_rol(rol)

            return usuario

    @classmethod
    def autenticar(cls, username: str, password_plana: str) -> Optional[Usuario]:
        """
        Método adaptador de clase para mantener compatibilidad directa con ui_login.py.
        """
        return cls.autenticar_usuario(username, password_plana)