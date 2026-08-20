# 1. Use Microsoft SDK to build the app
FROM ://microsoft.com AS build-env
WORKDIR /app

# Copy project files and restore dependencies
COPY *.csproj ./
RUN dotnet restore

# Copy remaining files and build production assets
COPY . ./
RUN dotnet publish -c Release -o out

# 2. Build runtime image
FROM ://microsoft.com
WORKDIR /app
COPY --from=build-env /app/out .

# Bind to Render's dynamic port environment
ENV ASPNETCORE_URLS=http://+:10000
EXPOSE 10000
ENTRYPOINT ["dotnet", "Mymvcapp.dll"]
