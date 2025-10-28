# Proyecto Smithy - Generación de Código Backend

Este proyecto utiliza Smithy para generar código backend a partir de definiciones de modelo. Incluye scripts para automatizar el proceso de generación.

## Estructura del Proyecto

```
.
├── openapi-generator-config.json
├── pom.xml
├── scripts
│   └── mvn-backend-generate.sh
├── smithy
│   └── user-service.smithy
└── smithy-build.json
```

## Prerrequisitos

### 3. Instalar Java 21 con SDKMAN

Si usas [SDKMAN](https://sdkman.io/) para gestionar versiones de Java, puedes instalar y usar Java 21.0.2-tem con:

```bash
sdk install java 21.0.2-tem
sdk use java 21.0.2-tem
```

### 2. Formateo automático de código Java

Para asegurar el formateo consistente del código Java generado, instala clang-format y configura la variable de entorno:

```bash
brew install clang-format
export JAVA_POST_PROCESS_FILE="/usr/local/bin/clang-format -i"
```

Puedes agregar la línea de export a tu archivo `~/.zshrc` o `~/.bashrc` para que se aplique automáticamente en cada terminal.

### 1. Instalación de Maven en macOS

#### Opción 1: Usando Homebrew (Recomendado)
```bash
# Instalar Homebrew si no lo tienes
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Maven
brew install maven

# Verificar instalación
mvn -version
```

#### Opción 2: Usando SDKMAN
```bash
# Instalar SDKMAN
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"

# Instalar Maven
sdk install maven

# Verificar instalación
mvn -version
```

#### Opción 3: Descarga manual
```bash
# Descargar Maven desde https://maven.apache.org/download.cgi
# Extraer el archivo descargado
tar -xzf apache-maven-*-bin.tar.gz
sudo mv apache-maven-* /usr/local/apache-maven

# Configurar variables de entorno
echo 'export M2_HOME=/usr/local/apache-maven' >> ~/.zshrc
echo 'export PATH=$M2_HOME/bin:$PATH' >> ~/.zshrc
source ~/.zshrc
```

### 2. Instalación de Gradle en macOS

#### Opción 1: Usando Homebrew (Recomendado)
```bash
brew install gradle

# Verificar instalación
gradle -version
```

#### Opción 2: Usando SDKMAN
```bash
sdk install gradle

# Verificar instalación
gradle -version
```

#### Opción 3: Descarga manual
```bash
# Descargar Gradle desde https://gradle.org/releases/
# Extraer el archivo descargado
unzip gradle-*-bin.zip
sudo mv gradle-* /usr/local/gradle

# Configurar variables de entorno
echo 'export GRADLE_HOME=/usr/local/gradle' >> ~/.zshrc
echo 'export PATH=$GRADLE_HOME/bin:$PATH' >> ~/.zshrc
source ~/.zshrc
```

### 3. Instalación de Smithy CLI

#### Opción 1: Usando Homebrew (Recomendado)
```bash
# Agregar el tap oficial de Smithy y instalar
brew tap smithy-lang/tap
brew install smithy-cli

# Verificar instalación
smithy --version
```

#### Opción 2: Usando el instalador automático
```bash
# Descargar e instalar Smithy CLI
curl -s https://dl.smithy.io/2.0.0/install.sh | bash

# La instalación agregará Smithy a tu PATH
# Puede que necesites reiniciar tu terminal o ejecutar:
source ~/.zshrc

# Verificar instalación
smithy --version
```

#### Opción 3: Usando el plugin de Maven (Alternativa)
Si prefieres no instalar Smithy CLI globalmente, puedes usar el plugin de Maven incluido en el proyecto:

```bash
# Desde el directorio raíz del proyecto
./mvnw smithy:build
```

## Configuración del Proyecto

### Verificar la instalación
Antes de ejecutar los scripts, verifica que todas las herramientas estén instaladas correctamente:

```bash
# Verificar Maven
mvn -version

# Verificar Gradle (opcional)
gradle -version

# Verificar Smithy CLI (si lo instalaste)
smithy --version
```

## Uso del Script de Generación

### Ejecutar el script de generación backend

```bash
# Navegar al directorio scripts
cd scripts

# Dar permisos de ejecución al script (si es necesario)
chmod +x mvn-backend-generate.sh

# Ejecutar el script
./mvn-backend-generate.sh
```

### Ejecución manual alternativa

Si el script no funciona, puedes ejecutar los comandos manualmente:

```bash
# Desde el directorio raíz del proyecto

# Opción 1: Usando Smithy CLI (si está instalado)
smithy build

# Opción 2: Usando Maven plugin
mvn clean compile
mvn smithy:build

# Opción 3: Generar OpenAPI específicamente
mvn smithy:build -Dmodels=openapi
```

## Flujo de Trabajo Recomendado

1. **Instalar las herramientas** usando Homebrew (método más sencillo):
   ```bash
   brew install maven gradle
   brew tap smithy-lang/tap && brew install smithy-cli
   ```

2. **Verificar la instalación**:
   ```bash
   mvn -version
   gradle -version
   smithy --version
   ```

3. **Generar el código**:
   ```bash
   cd scripts
   ./mvn-backend-generate.sh
   ```

## Solución de Problemas

### Problemas comunes en macOS

1. **Command not found: mvn**
   - Verifica que Maven esté instalado: `mvn -version`
   - Asegúrate de que el PATH esté configurado correctamente

2. **Error al instalar Smithy con Homebrew**
   ```bash
   # Actualizar Homebrew y reintentar
   brew update
   brew tap smithy-lang/tap
   brew install smithy-cli
   ```

3. **Permisos denegados al ejecutar scripts**
   ```bash
   chmod +x scripts/mvn-backend-generate.sh
   ```

4. **Problemas con Java**
   - Smithy requiere Java 8 o superior
   - Verifica tu versión de Java: `java -version`
   - Instala Java si es necesario: `brew install openjdk`

5. **Problemas con Smithy CLI**
   - Si Smithy CLI no funciona, usa el plugin de Maven:
   ```bash
   mvn smithy:build
   ```

### Configuración del Entorno de Desarrollo

Agrega estas líneas a tu `~/.zshrc` o `~/.bash_profile`:

```bash
# Maven (solo si instalaste manualmente)
export M2_HOME=/usr/local/apache-maven
export PATH=$M2_HOME/bin:$PATH

# Gradle (solo si instalaste manualmente)
export GRADLE_HOME=/usr/local/gradle
export PATH=$GRADLE_HOME/bin:$PATH

# Java
export JAVA_HOME=$(/usr/libexec/java_home)
```

Recargar la configuración:
```bash
source ~/.zshrc
```

## Soporte

Si encuentras problemas con la instalación o ejecución:

1. Verifica las versiones de las herramientas
2. Asegúrate de tener los permisos adecuados
3. Revisa los logs de error generados
4. Consulta la documentación oficial de cada herramienta

**Documentación oficial:**
- [Smithy](https://smithy.io/)
- [Smithy CLI Installation](https://smithy.io/2.0/guides/setup.html)
- [Maven](https://maven.apache.org/)
- [Gradle](https://gradle.org/)