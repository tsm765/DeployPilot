targetScope = 'resourceGroup'

@description('Azure region for the Container App.')
param location string = resourceGroup().location

@description('Deployment environment.')
param environment string = 'dev'

@description('Project name used for naming and tagging.')
param projectName string = 'deploypilot'

@description('Full ACR image reference including tag.')
param containerImage string


var commonTags = {
  Project: 'DeployPilot'
  Environment: environment
  ManagedBy: 'Bicep'
  CostProfile: 'student-low-cost'
}

var registryName = 'acr${projectName}${uniqueString(resourceGroup().id)}'
var identityName = 'id-${projectName}-${environment}'
var containerAppsEnvironmentName = 'cae-${projectName}-${environment}'
var containerAppName = 'ca-${projectName}-demo-${environment}'


resource containerRegistry 'Microsoft.ContainerRegistry/registries@2025-04-01' existing = {
  name: registryName
}


resource containerAppIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' existing = {
  name: identityName
}


resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2025-01-01' existing = {
  name: containerAppsEnvironmentName
}


resource containerApp 'Microsoft.App/containerApps@2025-01-01' = {
  name: containerAppName
  location: location
  tags: commonTags

  identity: {
    type: 'UserAssigned'

    userAssignedIdentities: {
      '${containerAppIdentity.id}': {}
    }
  }

  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    workloadProfileName: 'Consumption'

    configuration: {
      activeRevisionsMode: 'Single'

      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
        allowInsecure: false

        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }

      registries: [
        {
          server: containerRegistry.properties.loginServer
          identity: containerAppIdentity.id
        }
      ]
    }

    template: {
      containers: [
        {
          name: 'demo-api'
          image: containerImage

          resources: {
            cpu: any('0.25')
            memory: '0.5Gi'
          }
        }
      ]

      scale: {
        minReplicas: 0
        maxReplicas: 1
      }
    }
  }
}


output containerAppName string = containerApp.name
output containerAppFqdn string = containerApp.properties.configuration.ingress.fqdn
