# SWE.3 Detailed Design

| Document ID | INC-DIAG-16-SWE3-DD |
|-------------|---------------------|
| Issue | #16 |
| Component | sovd_adapter |
| Date | 2026-10-07 |

---

## 1. Module: registry.rs

### 1.1 Types

```rust
/// Wire format a resource produces and accepts.
pub enum PayloadFormat {
    Json,    // Values are JSON with optional schema
    Utf8,    // Values are UTF-8 text as JSON string
    Binary,  // Values are raw bytes as hex string
}

/// Why a resource could not be registered.
pub enum RegistrationError {
    DuplicateId(String),
    EmptyId,
}

/// One registered resource.
pub(crate) struct Entry {
    pub metadata: DataResourceMetadata,
    pub format: PayloadFormat,
    pub resource: Mutex<Box<dyn DataResource + Send>>,
}

/// Owns the diag_api resources a gateway component serves.
pub struct DataResourceRegistry {
    entries: IndexMap<String, Entry>,
}
```

### 1.2 Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `new()` | `() -> Self` | Create empty registry |
| `register()` | `(&mut self, meta, resource) -> Result<(), RegistrationError>` | Register JSON resource |
| `register_with_format()` | `(&mut self, meta, format, resource) -> Result<(), RegistrationError>` | Register with explicit format |
| `len()` | `(&self) -> usize` | Number of registered resources |
| `is_empty()` | `(&self) -> bool` | Check if empty |
| `get()` | `(&self, id) -> Option<&Entry>` | Lookup by ID |
| `entries()` | `(&self) -> impl Iterator<Item = &Entry>` | Iterate in order |

---

## 2. Module: provider.rs

### 2.1 Types

```rust
/// An opensovd_core::DataProvider serving resources from a registry.
pub struct SovdDataProvider {
    registry: DataResourceRegistry,
}
```

### 2.2 DataProvider Implementation

| Method | Implementation |
|--------|----------------|
| `list(filter)` | Map entries to Metadata, apply category/group/tag filters |
| `categories()` | Deduplicate categories from all entries (default impl) |
| `groups(category)` | Deduplicate groups, optionally filtered by category (default impl) |
| `read(id, schema)` | Lookup entry, create handle under lock, await, convert reply |
| `write(id, value)` | Check read-only, convert payload, create handle under lock, await |

### 2.3 Filter Logic

```rust
fn matches(meta: &Metadata, filter: &DataFilter) -> bool {
    let category_ok = filter.categories.is_empty()
        || filter.categories.contains(&meta.category);
    let group_ok = filter.groups.is_empty()
        || filter.groups.iter().any(|g| meta.groups.contains(g));
    let tag_ok = filter.tags.is_empty()
        || filter.tags.iter().any(|t| meta.tags.contains(t));
    category_ok && group_ok && tag_ok
}
```

---

## 3. Module: convert.rs

### 3.1 Metadata Conversion

```rust
pub fn metadata(meta: &DataResourceMetadata) -> Metadata {
    Metadata {
        id: meta.id.clone(),
        name: meta.name.clone(),
        category: meta.category.to_string(),
        translation_id: meta.translation_id.clone(),
        groups: meta.groups.clone().unwrap_or_default(),
        tags: Vec::new(),
        schema: None,
        is_readable: true,
        is_writable: !meta.read_only,
    }
}
```

### 3.2 JSON Conversion

```rust
// Different serde_json versions require string roundtrip
pub fn to_sovd_json(value: &diag_json::Value) -> Result<Value, DataError> {
    serde_json::from_str(&value.to_string())
}

pub fn to_diag_json(value: &Value) -> Result<diag_json::Value, DataError> {
    diag_json::from_str(&value.to_string())
}
```

### 3.3 Reply Encoding Selection

```rust
pub fn reply_encoding(format: PayloadFormat, include_schema: bool) -> ReplyMessageEncoding {
    match format {
        PayloadFormat::Json if include_schema => JSON(JsonSchemaRequired::Yes),
        PayloadFormat::Json => JSON(JsonSchemaRequired::No),
        PayloadFormat::Utf8 => UTF8,
        PayloadFormat::Binary => Binary,
    }
}
```

### 3.4 Error Mapping

| Source | Target |
|--------|--------|
| `ErrorCode::SOVD(generic)` | `DataError::Internal("{code}: {message}")` |
| `ErrorCode::UDS(nrc)` | `DataError::Internal("UDS negative response 0x{nrc:02X}")` |

---

## 4. Module: handle.rs

### 4.1 Read Handle Resolution

```rust
pub async fn resolve_read(handle: ReadValueHandle) -> DiagResult<ReadValueReply> {
    match handle {
        ReadValueHandle::Ready(result) => result,
        ReadValueHandle::Pending(future) => future.await,
    }
}
```

### 4.2 Write Handle Resolution

```rust
pub async fn resolve_write(handle: WriteValueHandle) -> Result<(), DiagDataError> {
    match handle {
        WriteValueHandle::Ready(result) => result,
        WriteValueHandle::Pending(future) => future.await,
    }
}
```

---

## 5. Module: cruise.rs (Gateway Example)

### 5.1 State Machine

```
        inject stuck
    +------------------+
    |                  v
[Passed] --debounce--> [PreFailed] --debounce--> [Failed]
    ^                                              |
    +--------- debounce <-------- [PrePassed] <---+
                                  clear stuck
```

### 5.2 Resources

| Resource | Read | Write |
|----------|------|-------|
| `vehicle_speed` | `{ "value": f64, "unit": "km/h" }` | - |
| `cruise_state` | `{ "state": str, "set_speed": f64 }` | - |
| `speed_sensor_fault_status` | `{ "fault": str, "status": str, "test_failed": bool, "confirmed": bool }` | - |
| `speed_sensor_stuck` | `{ "stuck": bool }` | `{ "stuck": bool }` |

---

## 6. Concurrency Design

### 6.1 Lock Scope

```rust
// CORRECT: Lock released before await
let pending = {
    let resource = entry.resource.lock()?;
    resource.read(args)  // Returns handle immediately
};  // Lock dropped here
let reply = handle::resolve_read(pending).await;  // Await without lock

// INCORRECT: Would deadlock on nested reads
let reply = entry.resource.lock()?.read(args).await;  // Lock held during await
```

### 6.2 Thread Safety

- `DataResourceRegistry` is `Send` (can move between threads)
- `SovdDataProvider` is `Send + Sync` (required by `DataProvider`)
- Resources are `Send` (stored in `Mutex<Box<dyn DataResource + Send>>`)

---

*Prepared by: EP1991 | Thinking_CAPs | Eclipse SDV Hackathon Chapter 4 2026*
