
# Copy project files and restore dependencies
COPY *.csproj ./
RUN dotnet restore

# Copy all source files and build the app
COPY . ./
RUN dotnet publish -c Release -o /app/publish /p:UseAppHost=false

# Stage 2: Runtime image
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final
WORKDIR /app

# Copy built app from the build stage
COPY --from=build /app/publish .

# Expose port 8080 (default for Render)
ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080

# Command to execute the application
ENTRYPOINT ["dotnet", "YourAppName.dll"]