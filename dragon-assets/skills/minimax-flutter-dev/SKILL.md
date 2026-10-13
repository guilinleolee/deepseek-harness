---
license: UNKNOWN
---

# MiniMax Flutter Development Skill

## Overview

Flutter cross-platform development with Riverpod/Bloc state management, covering widget patterns, navigation, and platform integration.

## Invocation

```
/minimax-flutter "构建Flutter应用"
[@18-01] 使用minimax-flutter实现跨平台开发
```

## Core Capabilities

### Project Structure

```
lib/
├── core/
│   ├── constants/
│   ├── theme/
│   ├── utils/
│   └── widgets/
├── features/
│   ├── auth/
│   │   ├── data/
│   │   ├── domain/
│   │   └── presentation/
│   └── ...
└── main.dart
```

### Widget Patterns

```dart
// Reusable widget
class PrimaryButton extends StatelessWidget {
  final String label;
  final VoidCallback onPressed;
  final bool isLoading;

  const PrimaryButton({
    required this.label,
    required this.onPressed,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: isLoading ? null : onPressed,
      child: isLoading
          ? const SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : Text(label),
    );
  }
}
```

### State Management - Riverpod

```dart
// Provider
final userRepositoryProvider = Provider<UserRepository>((ref) {
  return UserRepository();
});

// StateNotifier
class AuthNotifier extends StateNotifier<AuthState> {
  final UserRepository _repository;

  AuthNotifier(this._repository) : super(AuthState.initial());

  Future<void> login(String email, String password) async {
    state = state.copyWith(isLoading: true);
    try {
      final user = await _repository.login(email, password);
      state = state.copyWith(user: user, isLoading: false);
    } catch (e) {
      state = state.copyWith(error: e.toString(), isLoading: false);
    }
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.watch(userRepositoryProvider));
});

// Consumer
class LoginScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(authProvider);
    return ElevatedButton(
      onPressed: () => ref.read(authProvider.notifier).login(email, password),
      child: Text(state.isLoading ? 'Loading...' : 'Login'),
    );
  }
}
```

### State Management - Bloc

```dart
// Event
abstract class AuthEvent {}
class LoginRequested extends AuthEvent {
  final String email;
  final String password;
  LoginRequested({required this.email, required this.password});
}

// State
class AuthState {
  final bool isLoading;
  final User? user;
  final String? error;
}

// Bloc
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository _repository;

  AuthBloc(this._repository) : super(AuthState.initial()) {
    on<LoginRequested>(_onLoginRequested);
  }

  Future<void> _onLoginRequested(
    LoginRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(state.copyWith(isLoading: true));
    try {
      final user = await _repository.login(event.email, event.password);
      emit(state.copyWith(user: user, isLoading: false));
    } catch (e) {
      emit(state.copyWith(error: e.toString(), isLoading: false));
    }
  }
}
```

### Navigation - GoRouter

```dart
final router = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => HomeScreen(),
      routes: [
        GoRoute(
          path: 'profile/:id',
          builder: (context, state) => ProfileScreen(
            id: state.pathParameters['id']!,
          ),
        ),
      ],
    ),
  ],
);
```

## Integration with 天龙引擎

**Upgrades:**
- 18-01 移动开发工程师 V1.0 → V2.0: Flutter development

**Synergies:**
- turix-desktop-agent: Desktop automation
- e2e-testing: UI testing
