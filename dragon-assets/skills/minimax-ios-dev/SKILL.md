---
license: UNKNOWN
---

# MiniMax iOS Application Development Skill

## Overview

iOS app development using UIKit, SwiftUI, and SnapKit, emphasizing Apple Human Interface Guidelines and platform conventions.

## Invocation

```
/minimax-ios "构建iOS应用"
[@18-01] 使用minimax-ios实现原生iOS开发
[@04验证师] 使用minimax-ios验证UI测试
```

## Core Capabilities

### UIKit Components

```swift
// Navigation
let tabBar = UITabBarController()      // 3-5 top-level sections
let nav = UINavigationController()      // Drill-down navigation
present(sheet, animated: true)         // Focused tasks

// Lists - UICollectionView + DiffableDataSource
let datasource = UICollectionViewDiffableDataSource<Section, Item>(
  collectionView: collectionView
) { collectionView, indexPath, item in
  // Configure cell
}

// Interactions
let contextMenu = UIContextMenuInteraction(delegate: self)
let shareSheet = UIActivityViewController(activityItems: [...], applicationActivities: nil)
let searchBar = UISearchController(searchResultsController: nil)

// Layout
let stack = UIStackView(arrangedSubviews: [...])
stack.axis = .vertical
stack.spacing = 16
stack.distribution = .fill

// Custom shapes with CAShapeLayer
let path = UIBezierPath(roundedRect: rect, cornerRadius: 8)
let shapeLayer = CAShapeLayer()
shapeLayer.path = path.cgPath

// Modern UIButton
var config = UIButton.Configuration.filled()
config.title = "Submit"
config.image = UIImage(systemName: "arrow.right")
config.imagePadding = 8
button.configuration = config

// Dynamic Type
label.font = UIFont.preferredFont(forTextStyle: .headline)
label.adjustsFontForContentSizeCategory = true
```

### SwiftUI Components

```swift
// Navigation
TabView { ... }
  .tabItem { Label("Home", systemImage: "house") }

NavigationStack(path: $path) { ... }
  .navigationDestination(for: Route.self) { route in
    // Handle route
  }

// Presentations
.sheet(item: $item) { item in ... }
.alert("Title", isPresented: $showAlert) { ... }
.contextMenu(forSelectionType: Item.self) { ... }

// Lists
List(items) { item in ... }
  .listStyle(.insetGrouped)

// Features
.searchable(text: $searchText)
.shareLink(item: url)
.progressView()
.locationButton(.currentLocation) { ... }

// Adaptive
@Environment(\.dynamicTypeSize) var dynamicTypeSize
@Environment(\.accessibilityReduceMotion) var reduceMotion
```

### Layout Principles

```
Touch targets: Minimum 44pt
Spacing: 8pt increments (8, 16, 24, 32, 40, 48)
Safe areas: Always respect safeAreaLayoutGuide
Screen sizes: Support iPhone SE (375pt) to Pro Max (430pt)
```

### Typography

```swift
// UIKit
label.font = UIFont.preferredFont(forTextStyle: .headline)
label.adjustsFontForContentSizeCategory = true

// SwiftUI
Text("Title")
  .font(.headline)  // Semantic styles

// Custom fonts with metrics
let descriptor = UIFontDescriptor.preferredFontDescriptor(withTextStyle: .body)
let metrics = UIFontMetrics(descriptor.pointSize)
label.font = metrics.scaledFont(for: customFont)
```

### Accessibility

```swift
// VoiceOver
button.accessibilityLabel = "Submit form"
button.accessibilityHint = "Double tap to submit"
button.accessibilityTraits = .button

// Reduce motion
@Environment(\.accessibilityReduceMotion) var reduceMotion
if reduceMotion {
  // Disable animations
}

// Logical reading order
view.accessibilitySortPriority = 10

// Alternative gesture paths
// Ensure all gestures have alternative access
```

### Privacy

```swift
// Request in context, not at launch
// Provide explanation before system dialog
// Support Sign in with Apple
// Respect ATT denial

// AVFoundation permissions
AVCaptureDevice.requestAccess(for: .camera) { granted in
  // Handle response
}
```

## Integration with 天龙引擎

**Upgrades:**
- 18-01 移动开发工程师 V1.0 → V2.0: iOS native development

**Synergies:**
- turix-desktop-agent: Desktop automation testing
- e2e-testing: UI testing patterns
