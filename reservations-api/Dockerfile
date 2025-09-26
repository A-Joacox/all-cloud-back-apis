FROM openjdk:17-jdk-slim

WORKDIR /app

# Copiar pom.xml y descargar dependencias
COPY pom.xml .
RUN apt-get update && apt-get install -y maven && rm -rf /var/lib/apt/lists/*
RUN mvn dependency:go-offline -B

# Copiar código fuente
COPY src ./src

# Construir la aplicación
RUN mvn clean package -DskipTests

# Crear imagen final
FROM openjdk:17-jre-slim

WORKDIR /app

# Copiar JAR construido
COPY --from=0 /app/target/*.jar app.jar

# Exponer puerto
EXPOSE 3003

# Comando para iniciar la aplicación
CMD ["java", "-jar", "app.jar"]