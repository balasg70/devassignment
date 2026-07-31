# Multi-stage build for Spring PetClinic
# Stage 1: Build the application
FROM maven:3.8-openjdk-17-slim AS builder

WORKDIR /app

# Copy Maven project files
COPY pom.xml .
RUN mvn dependency:go-offline

# Copy source code and build
COPY src ./src
RUN mvn clean package -DskipTests

# Stage 2: Runtime image
FROM eclipse-temurin:17-jre-alpine

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set working directory
WORKDIR /app

# Copy JAR from builder
COPY --from=builder /app/target/*.jar app.jar

# Create directory for logs
RUN mkdir -p /app/logs && chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Environment variables for configuration
ENV SPRING_PROFILES_ACTIVE=default \
    DATABASE_URL=jdbc:h2:mem:testdb \
    DATABASE_USERNAME=sa \
    DATABASE_PASSWORD= \
    JVM_OPTS="-Xmx512m -Xms256m"

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/actuator/health || exit 1

# Entry point
ENTRYPOINT ["sh", "-c", "java $JVM_OPTS -jar app.jar"]