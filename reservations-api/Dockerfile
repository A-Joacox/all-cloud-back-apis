FROM eclipse-temurin:17-jdk-alpine

WORKDIR /app

# Copiar pom.xml y descargar dependencias
COPY pom.xml .
RUN apk add --no-cache maven
RUN mvn dependency:go-offline -B

# Copiar código fuente
COPY src ./src

# Construir la aplicación
RUN mvn clean package -DskipTests

# Crear imagen final
FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

# Copiar JAR construido
COPY --from=0 /app/target/*.jar app.jar

# Exponer puerto
EXPOSE 3003

# Comando para iniciar la aplicación
CMD ["java", "-jar", "app.jar"]