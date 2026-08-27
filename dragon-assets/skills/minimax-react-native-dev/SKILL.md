---
license: UNKNOWN
---

# MiniMax React Native Development Skill

## Overview

React Native development with Expo, covering components, navigation, animations, forms, and native capabilities.

## Invocation

```
/minimax-react-native "构建React Native应用"
[@18-01] 使用minimax-react-native实现移动开发
```

## Core Capabilities

### Project Setup

```bash
# Expo (recommended)
npx create-expo-app@latest MyApp
npx expo start

# Bare React Native
npx @react-native-community/cli init MyApp

# Key dependencies
npx expo install react-native-reanimated
npx expo install react-native-gesture-handler
npx expo install @react-navigation/native
```

### Components

```tsx
// Reusable component
interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary';
  loading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  loading,
}) => {
  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={loading}
      style={[
        styles.button,
        variant === 'primary' ? styles.primary : styles.secondary,
      ]}
    >
      {loading ? (
        <ActivityIndicator color="#fff" />
      ) : (
        <Text style={styles.text}>{title}</Text>
      )}
    </TouchableOpacity>
  );
};
```

### Navigation

```tsx
// Stack Navigator
import { createNativeStackNavigator } from '@react-navigation/native-stack';

const Stack = createNativeStackNavigator();

function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen
          name="Profile"
          component={ProfileScreen}
          options={{ title: 'User Profile' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

// Tab Navigator
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

const Tab = createBottomTabNavigator();

function TabNavigator() {
  return (
    <Tab.Navigator>
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}
```

### Forms with React Hook Form

```tsx
import { useForm } from 'react-hook-form';

interface FormData {
  email: string;
  password: string;
}

export const LoginForm = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>();

  const onSubmit = (data: FormData) => {
    console.log(data);
  };

  return (
    <Form onSubmit={handleSubmit(onSubmit)}>
      <Input
        {...register('email', {
          required: 'Email is required',
          pattern: { value: /^\S+@\S+$/i, message: 'Invalid email' }
        })}
        placeholder="Email"
      />
      {errors.email && <Text>{errors.email.message}</Text>}

      <Input
        {...register('password', {
          required: 'Password is required',
          minLength: { value: 6, message: 'Min 6 characters' }
        })}
        placeholder="Password"
        secureTextEntry
      />
      {errors.password && <Text>{errors.password.message}</Text>}

      <Button title="Submit" onPress={handleSubmit(onSubmit)} />
    </Form>
  );
};
```

### Animations with Reanimated

```tsx
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withTiming,
  interpolate,
} from 'react-native-reanimated';

export const AnimatedButton = ({ onPress, children }) => {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  return (
    <Animated.View style={animatedStyle}>
      <Pressable
        onPressIn={() => { scale.value = withSpring(0.95); }}
        onPressOut={() => { scale.value = withSpring(1); }}
        onPress={onPress}
      >
        {children}
      </Pressable>
    </Animated.View>
  );
};
```

## Integration with 天龙引擎

**Upgrades:**
- 18-01 移动开发工程师 V1.0 → V2.0: React Native development
