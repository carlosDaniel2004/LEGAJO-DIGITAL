# Documentación Técnica del Sistema de Legajo Digital

Este documento proporciona una descripción detallada de la arquitectura, componentes y flujos de trabajo del sistema de Legajo Digital. Está diseñado para servir como guía de referencia para los desarrolladores y arquitectos de software.

## Tabla de Contenidos

1.  [Arquitectura General](#1-arquitectura-general)
2.  [Capa de Dominio (`app/domain`)](#2-capa-de-dominio-appdomain)
3.  [Capa de Aplicación (`app/application`)](#3-capa-de-aplicación-appapplication)
4.  [Capa de Infraestructura (`app/infrastructure`)](#4-capa-de-infraestructura-appinfrastructure)
5.  [Capa de Presentación (`app/presentation`)](#5-capa-de-presentación-apppresentation)
6.  [Configuración y Arranque](#6-configuración-y-arranque)
7.  [Flujo de una Solicitud](#7-flujo-de-una-solicitud)

## 1. Arquitectura General

El sistema está construido siguiendo una **Arquitectura en Capas (Layered Architecture)**, un diseño que promueve la **Separación de Responsabilidades (Separation of Concerns)**. Esta arquitectura está fuertemente influenciada por los principios de **Domain-Driven Design (DDD)** y **Clean Architecture**.

El objetivo principal es aislar la lógica de negocio (el dominio) de las tecnologías externas (como la base de datos o la interfaz de usuario). Esto hace que el sistema sea más fácil de mantener, probar y escalar.

La estructura se puede visualizar como una serie de capas concéntricas, donde las dependencias fluyen hacia adentro:

- **Capa de Presentación**: La interfaz de usuario (UI).
- **Capa de Aplicación**: Orquesta los casos de uso.
- **Capa de Dominio**: El corazón de la lógica de negocio.
- **Capa de Infraestructura**: Implementaciones técnicas (base de datos, APIs, etc.).

![Diagrama de Arquitectura en Capas](https://i.imgur.com/s9b4s2P.png)

### Principios Clave:

- **Regla de Dependencia**: El código fuente solo puede tener dependencias que apunten hacia adentro. Nada en una capa interna puede saber nada sobre una capa externa. Por ejemplo, el dominio no sabe qué base de datos se está utilizando.
- **Abstracción**: Las capas externas (como la infraestructura) implementan interfaces (contratos) definidas en las capas internas (el dominio). Esto permite intercambiar implementaciones sin afectar la lógica de negocio.

## 2. Capa de Dominio (`app/domain`)

Esta capa es el **corazón de la aplicación**. Contiene toda la lógica de negocio, las reglas y las entidades que son independientes de cualquier tecnología externa. No sabe nada sobre la base de datos, la web o cualquier otro detalle de implementación.

### 2.1. Modelos (`app/domain/models`)

Este directorio contiene las **Entidades de Negocio**. Son clases de Python que representan los conceptos fundamentales del sistema.

-   `usuario.py`: Representa a un usuario del sistema, con sus credenciales, roles y estado.
-   `personal.py`: Modela a un empleado de la organización, conteniendo toda su información personal.
-   `contrato.py`: Define la relación contractual de un empleado, incluyendo tipo, fechas y condiciones.
-   `documento.py`: Representa un documento físico o digital asociado a un legajo.
-   `legajo_seccion.py`: Modela la estructura y secciones que componen el legajo de un empleado.
-   `rol.py`: Define los roles y permisos dentro de la aplicación (ej. RRHH, Sistemas).
-   `solicitud_modificacion.py`: Representa una solicitud de un usuario para cambiar un dato en un legajo, que requiere aprobación.
-   *(y otros modelos que definen conceptos como `capacitacion`, `estudio`, `licencia`, etc.)*

### 2.2. Repositorios (`app/domain/repositories`)

Este directorio contiene las **Interfaces de Repositorio**. Una interfaz es un "contrato" que define qué operaciones de datos se pueden realizar con los modelos del dominio, pero no cómo se realizan. Esto es clave para la abstracción.

-   `i_usuario_repository.py`: Define métodos como `buscar_por_username`, `crear_usuario`, `actualizar_rol`, etc.
-   `i_personal_repository.py`: Define métodos para buscar, crear y actualizar la información del personal.
-   `i_auditoria_repository.py`: Define cómo se deben registrar los eventos de auditoría en el sistema.

Estas interfaces aseguran que la capa de aplicación pueda solicitar datos sin conocer los detalles de la base de datos subyacente.

## 3. Capa de Aplicación (`app/application`)

Esta capa actúa como un **orquestador**. No contiene lógica de negocio, sino que dirige a los objetos del dominio para que la ejecuten en respuesta a las solicitudes de la capa de presentación. Es el puente entre la UI y el Dominio.

### 3.1. Servicios (`app/application/services`)

Los servicios de aplicación implementan los **casos de uso** del sistema. Cada servicio encapsula una funcionalidad específica.

-   `usuario_service.py`: Maneja la lógica relacionada con la autenticación, 2FA (Two-Factor Authentication) y la gestión de sesiones de usuario.
-   `user_management_service.py`: Se encarga de los casos de uso administrativos sobre usuarios, como la creación, actualización de roles y cambio de estado.
-   `legajo_service.py`: Orquesta las operaciones sobre los legajos del personal, como la obtención de datos completos, la adición de documentos, etc.
-   `audit_service.py`: Proporciona una interfaz sencilla para que el resto de la aplicación pueda registrar eventos de auditoría importantes.
-   `email_service.py`: Abstrae el envío de correos electrónicos, como los códigos de 2FA o notificaciones.
-   `backup_service.py`: Contiene la lógica para ejecutar y registrar las copias de seguridad de la base de datos.
-   `solicitud_service.py`: Gestiona la creación y procesamiento de solicitudes de modificación de datos.
-   `workflow_service.py`: Maneja la lógica de los flujos de aprobación para las solicitudes.

### 3.2. Formularios (`app/application/forms.py`)

Este archivo define las clases de formularios utilizando la librería `Flask-WTF`. Su responsabilidad es:

1.  **Definir los campos** que se mostrarán en la interfaz de usuario.
2.  **Validar los datos** enviados por el usuario (ej. que un email tenga el formato correcto, que un campo requerido no esté vacío).

Esto asegura que los datos que llegan a los servicios de aplicación ya han sido limpiados y validados, evitando que lógica de validación de UI contamine las capas internas.

## 4. Capa de Infraestructura (`app/infrastructure` y `app/database`)

Esta capa contiene las **implementaciones concretas** de las tecnologías externas. Es el "cómo" se hacen las cosas que las capas internas solo definen.

### 4.1. Persistencia (`app/infrastructure/persistence`)

Aquí es donde se implementan las interfaces de repositorio definidas en el dominio.

-   `sqlserver_repository.py`: Esta clase contiene el código **específico para SQL Server**. Implementa las interfaces como `IUsuarioRepository` y traduce sus métodos (`buscar_por_username`) a consultas SQL (`SELECT * FROM Usuario WHERE username = ?`). Si el día de mañana se decidiera migrar a PostgreSQL, solo habría que crear un nuevo archivo `postgresql_repository.py` que implemente las mismas interfaces, sin tocar el dominio ni la aplicación.

### 4.2. Conector de Base de Datos (`app/database/connector.py`)

Este componente se encarga de una única responsabilidad: **gestionar la conexión con la base de datos**.

-   Lee la cadena de conexión desde la configuración de la aplicación.
-   Utiliza la librería `pyodbc` para establecer y mantener un pool de conexiones.
-   Proporciona métodos para obtener una conexión activa y ejecutar consultas, gestionando transacciones (commit, rollback) y el cierre de conexiones.

Abstrae el manejo de la conexión para que los repositorios no tengan que preocuparse por los detalles de bajo nivel de `pyodbc`.

## 5. Capa de Presentación (`app/presentation`)

Esta es la capa más externa, responsable de interactuar con el usuario final. En esta aplicación web, se encarga de manejar las peticiones HTTP y renderizar las plantillas HTML.

### 5.1. Rutas (`app/presentation/routes`)

Las rutas definen los endpoints (URLs) de la aplicación. El código está organizado en **Blueprints** de Flask, que permiten agrupar rutas por funcionalidad, manteniendo el código ordenado.

-   `auth_routes.py`: Maneja las URLs de autenticación, como `/login`, `/logout` y `/verify_2fa`.
-   `sistemas_routes.py`: Contiene los endpoints para el panel de administración del sistema (gestión de usuarios, auditoría, backups, etc.).
-   `rrhh_routes.py`: Define las rutas para el personal de Recursos Humanos, como la visualización de legajos y la gestión de personal.
-   `legajo_routes.py`: Rutas relacionadas con la gestión específica del contenido de un legajo.
-   `report_routes.py`: Endpoints para la generación de reportes.

Las funciones dentro de estos archivos actúan como **controladores**: reciben la petición, la delegan al servicio de aplicación correspondiente y, con el resultado, seleccionan y renderizan la plantilla adecuada.

### 5.2. Plantillas (`app/presentation/templates`)

Este directorio contiene los archivos HTML que conforman la interfaz de usuario. Se utiliza el motor de plantillas **Jinja2**, que permite:

-   **Herencia de plantillas**: Se define una `base.html` o `dashboard.html` con la estructura común (header, footer, sidebar), y las páginas específicas heredan de ella, rellenando solo los bloques de contenido.
-   **Lógica simple**: Permite usar bucles (`for`), condicionales (`if`) y mostrar variables pasadas desde el controlador (ej. `{{ current_user.username }}`).
-   **Reutilización de componentes**: Se pueden crear componentes pequeños (como `_form_helpers.html`) e incluirlos en varias páginas.

### 5.3. Archivos Estáticos (`app/presentation/static`)

Contiene los archivos que no cambian, como:

-   `css`: Hojas de estilo para dar formato y diseño a la aplicación.
-   `js`: Archivos JavaScript para la interactividad en el lado del cliente.
-   `img`: Imágenes y otros recursos gráficos.

## 6. Configuración y Arranque

Estos archivos son responsables de inicializar y configurar la aplicación Flask, así como de ensamblar todas las capas.

-   `run.py`: Es el **punto de entrada** para ejecutar la aplicación. Su única responsabilidad es importar la función `create_app` y poner en marcha el servidor de desarrollo de Flask.

-   `config.py`: Define una clase `Config` que contiene todas las variables de configuración de la aplicación, como las claves secretas, la cadena de conexión a la base de datos, y la configuración del servidor de correo. Carga variables sensibles desde un archivo `.env` para no exponerlas en el código fuente.

-   `app/__init__.py`: Contiene la función `create_app()`, que actúa como una **fábrica de la aplicación**. Este es un patrón muy importante en Flask que permite crear múltiples instancias de la aplicación con diferentes configuraciones (por ejemplo, para producción, desarrollo o pruebas). Sus responsabilidades son:
    1.  Crear la instancia principal de la aplicación Flask.
    2.  Cargar la configuración desde el objeto `Config`.
    3.  Inicializar las extensiones de Flask (como `LoginManager` para la sesión de usuario).
    4.  **Realizar la Inyección de Dependencias**: Aquí es donde se "cablea" todo el sistema. Se crean las instancias de los repositorios (la implementación de SQL Server) y los servicios, inyectando las dependencias necesarias en cada uno (por ejemplo, se le pasa el repositorio de usuarios al servicio de usuarios).
    5.  Registrar los **Blueprints** de las rutas.

## 7. Flujo de una Solicitud

Para consolidar la comprensión de la arquitectura, sigamos el viaje de una petición a través del sistema.

**Caso de Uso**: Un usuario de RRHH solicita ver el legajo completo de un empleado con un DNI específico.

1.  **Petición HTTP (Navegador)**: El usuario hace clic en un enlace, generando una petición `GET` a la URL `/rrhh/ver_legajo/12345678`.

2.  **Capa de Presentación (Rutas)**:
    -   Flask recibe la petición.
    -   El blueprint de RRHH en `rrhh_routes.py` captura esta URL con una regla como `@rrhh_blueprint.route('/ver_legajo/<dni>')`.
    -   La función controladora asociada, `ver_legajo(dni)`, se ejecuta.

3.  **Capa de Aplicación (Servicios)**:
    -   El controlador no contiene lógica. Delega inmediatamente la tarea a un servicio de aplicación: `legajo_service.obtener_legajo_completo(dni)`.
    -   El `legajo_service` orquesta la operación. Podría, por ejemplo, llamar primero al `audit_service` para registrar el intento de acceso.

4.  **Capa de Dominio (Interfaces de Repositorio)**:
    -   El `legajo_service` necesita obtener los datos del empleado. Para ello, invoca un método de la **interfaz** de repositorio que tiene inyectada: `self.personal_repo.buscar_por_dni(dni)`.
    -   Es importante destacar que el servicio **no sabe** que está hablando con SQL Server. Solo conoce el contrato definido por la interfaz.

5.  **Capa de Infraestructura (Implementación del Repositorio)**:
    -   El motor de inyección de dependencias (configurado en `app/__init__.py`) determinó que `self.personal_repo` es una instancia de `SqlServerRepository`.
    -   Se ejecuta el método `buscar_por_dni` en `sqlserver_repository.py`, que construye y ejecuta la consulta SQL: `SELECT * FROM Personal WHERE dni = ?`.

6.  **Retorno de Datos y Modelado (Dominio)**:
    -   La base de datos devuelve los datos crudos.
    -   El `SqlServerRepository` utiliza estos datos para construir una instancia del modelo de dominio `Personal` (definido en `app/domain/models/personal.py`).

7.  **Flujo de Retorno**:
    -   El objeto `Personal` viaja de vuelta a través de las capas: Infraestructura -> Aplicación -> Presentación.

8.  **Renderizado (Presentación)**:
    -   La función controladora `ver_legajo(dni)` recibe el objeto `Personal`.
    -   Llama a `render_template('rrhh/ver_legajo_completo.html', personal=objeto_personal)`, pasando el objeto a la plantilla.
    -   Jinja2 utiliza los datos del objeto para rellenar el HTML.

9.  **Respuesta HTTP (Navegador)**: El servidor envía el HTML renderizado de vuelta al navegador del usuario, que ve la página completa del legajo.

---

Este flujo asegura que todas las solicitudes sean manejadas de manera consistente y que la lógica de negocio esté centralizada en los servicios de aplicación y el dominio.

---
