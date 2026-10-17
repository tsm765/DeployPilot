targetScope = 'resourceGroup'

@description('Azure region for DeployPilot resources.')
param location string = resourceGroup().location

@description('Deployment environment.')
param environment string = 'dev'

@description('Project name used for naming and tagging.')
param projectName string = 'deploypilot'

@description('GitHub repository owner.')
param githubOwner string

@description('Immutable GitHub repository owner ID.')
param githubOwnerId string

@description('GitHub repository name.')
param githubRepository string

@description('Immutable GitHub repository ID.')
param githubRepositoryId string

@description('GitHub branch allowed to authenticate to Azure.')
param githubBranch string = 'main'

var commonTags = {
  Project: 'DeployPilot'
  Environment: environment
  ManagedBy: 'Bicep'
  CostProfile: 'student-low-cost'
}

var registryName = 'acr${projectName}${uniqueString(resourceGroup().id)}'
var identityName = 'id-${projectName}-${environment}'
var githubIdentityName = 'id-${projectName}-github-${environment}'
var containerAppsEnvironmentName = 'cae-${projectName}-${environment}'
var githubOidcSubject = 'repo:${githubOwner}@${githubOwnerId}/${githubRepository}@${githubRepositoryId}:ref:refs/heads/${githubBranch}'

@description('Built-in AcrPull role definition ID.')
var acrPullRoleDefinitionId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '7f951dda-4ed3-4680-a7ca-43fe172d538d'
)

@description('Built-in AcrPush role definition ID.')
var acrPushRoleDefinitionId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '8311e382-0749-4cb8-b61a-304f252e45ec'
)

@description('Built-in Container Apps Contributor role definition ID.')
var containerAppsContributorRoleDefinitionId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '358470bc-b998-42bd-ab17-a7e34c199c0f'
)

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2025-04-01' = {
  name: registryName
  location: location
  tags: commonTags

  sku: {
    name: 'Standard'
  }

  properties: {
    adminUserEnabled: false
    anonymousPullEnabled: false
    publicNetworkAccess: 'Enabled'
  }
}

resource containerAppIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: identityName
  location: location
  tags: commonTags
}

resource githubDeployIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: githubIdentityName
  location: location
  tags: commonTags
}

resource githubFederatedCredential 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2024-11-30' = {
  parent: githubDeployIdentity
  name: 'github-main'
  properties: {
    audiences: [
      'api://AzureADTokenExchange'
    ]
    issuer: 'https://token.actions.githubusercontent.com'
    subject: githubOidcSubject
  }
}

resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(
    containerRegistry.id,
    containerAppIdentity.id,
    'AcrPull'
  )
  scope: containerRegistry

  properties: {
    principalId: containerAppIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: acrPullRoleDefinitionId
  }
}

resource githubAcrPushRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(
    containerRegistry.id,
    githubDeployIdentity.id,
    'AcrPush'
  )

  scope: containerRegistry

  properties: {
    principalId: githubDeployIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: acrPushRoleDefinitionId
  }
}

resource githubContainerAppsContributorRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(
    resourceGroup().id,
    githubDeployIdentity.id,
    'ContainerAppsContributor'
  )

  properties: {
    principalId: githubDeployIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: containerAppsContributorRoleDefinitionId
  }
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2025-01-01' = {
  name: containerAppsEnvironmentName
  location: location
  tags: commonTags

  properties: {

    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]

    zoneRedundant: false
  }
}

output deploymentLocation string = location
output deploymentEnvironment string = environment

output containerRegistryName string = containerRegistry.name
output containerRegistryLoginServer string = containerRegistry.properties.loginServer

output managedIdentityName string = containerAppIdentity.name
output managedIdentityId string = containerAppIdentity.id
output managedIdentityPrincipalId string = containerAppIdentity.properties.principalId

output githubDeployIdentityName string = githubDeployIdentity.name
output githubDeployIdentityId string = githubDeployIdentity.id
output githubDeployIdentityClientId string = githubDeployIdentity.properties.clientId
output githubDeployIdentityPrincipalId string = githubDeployIdentity.properties.principalId

output containerAppsEnvironmentName string = containerAppsEnvironment.name
output containerAppsEnvironmentId string = containerAppsEnvironment.id
output githubOidcSubject string = githubOidcSubject
