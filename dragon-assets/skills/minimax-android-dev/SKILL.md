---
license: UNKNOWN
---

# MiniMax Android Native Development Skill

## Overview

Android native app development using Kotlin/Jetpack Compose with Material Design 3, covering project setup, architecture standards, and build configuration.

## Invocation

```
/minimax-android "构建Android应用"
[@18-01] 使用minimax-android实现原生Android开发
[@04验证师] 使用minimax-android验证测试覆盖率
```

## Core Capabilities

### Project Initialization

```bash
# Check project state
./gradlew tasks --all  # Verify Gradle wrapper works

# Required files
gradle.properties          # AndroidX config
settings.gradle.kts       # Project settings
build.gradle.kts          # Build configuration
app/build.gradle.kts      # App module
AndroidManifest.xml        # App manifest
```

### Build Configuration

```kotlin
// gradle.properties
android.useAndroidX=true
android.enableJetifier=true
kotlin.code.style=official
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8

// Build variants
// {flavor}{BuildType} = devDebug, prodRelease, etc.
```

### Kotlin Standards

```kotlin
// Null Safety - NEVER use !! operator
val name: String? = null
val length = name?.length ?: 0

// Threading
Main → Dispatchers.Main
Network/IO → Dispatchers.IO
Compute → Dispatchers.Default

// Exception Handling - Return Result<T>
suspend fun fetchUser(id: String): Result<User> {
  return try {
    val response = api.getUser(id)
    Result.success(response.toUser())
  } catch (e: Exception) {
    Result.failure(e)
  }
}

// Server DTOs - ALL fields nullable
data class UserDto(
  val id: String? = null,
  val name: String? = null,
  val email: String? = null
)
```

### Compose Rules

```kotlin
// ONLY call @Composable from composable context
@Composable
fun MyScreen() {
  val viewModel = viewModel<MyViewModel>() // ✅ OK

  // ❌ WRONG: Creating ViewModels inside composable
  // val vm = remember { MyViewModel() }
}

// Use LaunchedEffect for async operations
@Composable
fun MyScreen(viewModel: MyViewModel) {
  LaunchedEffect(Unit) {
    viewModel.loadData()
  }
}
```

### Resource Naming

**Prefix all resources to avoid Android reserved names:**

```
❌ AVOID: background, icon, view, button, text, android, app, dialog, popup
✅ USE: app_background, ic_home, btn_submit, txt_title, dlg_confirm, pmt_info
```

### Material Design 3

```kotlin
// Touch targets: 48dp minimum (56dp for kids apps)
// Spacing: 8dp grid system
// Contrast: 4.5:1 for body text
// Startup: < 2 seconds or show progress indicator
// Dark theme: REQUIRED support
```

## Key Commands

```bash
# Build
./gradlew assembleDebug        # Debug APK
./gradlew assembleRelease      # Release APK
./gradlew clean assembleDebug   # Clean rebuild

# Dependencies
./gradlew :app:dependencies   # Check dependency tree
./gradlew :app:dependencyUpdates # Check for updates

# Verification
./gradlew lint                # Run lint
./gradlew test                # Unit tests
./gradlew connectedAndroidTest  # Instrumented tests
```

## Architecture Pattern

```kotlin
// Feature-first structure
app/src/main/java/com/example/
├── features/
│   ├── login/
│   │   ├── data/
│   │   │   ├── LoginRepository.kt
│   │   │   ├── LoginApi.kt
│   │   │   └── dto/
│   │   ├── domain/
│   │   │   ├── model/
│   │   │   ├── repository/
│   │   │   └── usecase/
│   │   └── presentation/
│   │       ├── LoginScreen.kt
│   │       ├── LoginViewModel.kt
│   │       └── LoginUiState.kt
│   └── ...
└── shared/
    ├── ui/
    ├── data/
    └── di/
```

## Integration with 天龙引擎

**Upgrades:**
- 18-01 移动开发工程师 V1.0 → V2.0: Android native development

**Synergies:**
- turix-desktop-agent: Desktop automation testing
- e2e-testing: UI testing patterns
- playwright-skill: Browser automation
