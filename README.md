# URL-shorty
A serverless URL shortening service built using Azure Functions and Azure Table Storage.
Project Overview
This URL shortener demonstrates a modern, serverless cloud architecture on Azure. It allows users to convert long, unwieldy URLs into short, easy-to-share links with automatic redirection to the original destination.
Key Features

Create shortened URLs through a clean, responsive interface
Automatic redirection to original URLs
Persistence through Azure Table Storage
Serverless architecture with Azure Functions
No infrastructure management required

## Technology Stack

Backend: Azure Functions with Python
Data Storage: Azure Table Storage
Frontend: HTML, CSS, JavaScript
Hosting: Azure Static Web Apps
Architecture: Serverless microservices

## Project Architecture
The application follows a modern serverless architecture:

+ Frontend (Static Web App) - Provides the user interface for URL submission
+ API (Azure Functions) - Processes requests to create and redirect URLs
+ Storage (Azure Table Storage) - Persists URL mappings with minimal cost

This architecture demonstrates cloud-native design principles with:

Pay-per-execution cost model
Automatic scaling
No server management
Built-in high availability

Learning Outcomes
Through this project, I've gained hands-on experience with:

+ Implementing serverless applications in Azure
+ Working with Azure Table Storage for cost-effective data persistence
+ Managing cloud resources using the Azure portal and tools
+ Building responsive frontends that interact with cloud backends
+ Understanding API design and cloud architecture patterns
