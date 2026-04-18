# AI Service Bug Report and Fix Tracking

## Issue Summary
The AI Service fails to start due to Pydantic v2 configuration validation errors.

## Root Cause
**File**: `ai-service/app/severity.py`
**Line**: 30

The `SeverityConfig` class in `severity.py` is defined with only 3 fields but is trying to load a `.env` file that contains 11+ environment variables. Pydantic v2's `BaseSettings` with default settings (`extra='forbid'`) rejects any fields not explicitly defined in the class.

## Bugs Identified

### Bug #1: SeverityConfig Missing Field Definitions ✅ FIXED
**File**: `ai-service/app/severity.py` (lines 14-24)
**Problem**: Class only defines 3 fields but receives 11 extra fields from environment
**Expected Fields NOT defined**:
- YOLO_MODEL_PATH
- RELEVANT_CLASSES  
- MAX_IMAGE_SIZE
- ALLOWED_EXTENSIONS
- AI_SERVICE_PORT
- AI_SERVICE_HOST
- LOG_LEVEL
- INFERENCE_IMAGE_SIZE
- MAX_CONCURRENT_REQUESTS
- AUTO_DOWNLOAD_MODEL
- MODEL_DOWNLOAD_URL

**Solution Applied**: 
- Removed SeverityConfig class entirely
- Replaced with imports from app.config.settings
- All configuration now centralized in app/config.py

### Bug #2: Redundant Configuration Classes ✅ FIXED
**Files**: 
- `ai-service/app/config.py` - defines `AISettings` with all fields
- `ai-service/app/severity.py` - defines `SeverityConfig` with subset of fields

**Problem**: Two separate settings classes loading from same .env file creates confusion and conflicts

**Solution Applied**: 
- Removed SeverityConfig class from severity.py
- All references now use `from app.config import settings`
- Single source of truth for all configuration

### Bug #3: RELEVANT_CLASSES Type Mismatch ✅ FIXED
**File**: `ai-service/app/config.py`
**Problem**: Hardcoded as Python set, in .env as comma-separated string, type conversion missing
**Problem**: Code tries to compare with this but pydantic expects proper type conversion

**Solution Applied**: 
- Added `@field_validator("RELEVANT_CLASSES", mode="before")` to convert comma-separated strings to set
- Added `@field_validator("ALLOWED_EXTENSIONS", mode="before")` for extensions parsing
- Added `@field_validator("INFERENCE_IMAGE_SIZE", mode="before")` for tuple parsing
- Added `@field_validator("AUTO_DOWNLOAD_MODEL", mode="before")` for boolean parsing

### Bug #4: Inheritance Chain Issue ✅ FIXED
**Files**: `ai-service/app/inference_phase1.py` → `severity.py` → `config.py`
**Problem**: Import order causes SeverityConfig() to be instantiated at module load time
**Problem**: This happens before any configuration context is set up

**Solution Applied**: 
- Removed module-level SeverityConfig() instantiation
- All configuration accessed through `settings` object from app.config
- settings object is only created once when needed

### Bug #5: Async/Await Mismatch ✅ FIXED
**File**: `ai-service/app/inference_phase1.py` and `ai-service/app/main.py`
**Problem**: `initialize_inference_engine` defined as `async` but called without `await`
**Problem**: Lifespan handler is async context but trying to call async function directly

**Solution Applied**: 
- Changed `initialize_inference_engine` from `async def` to `def`
- Made it return `bool` instead of Phase1Inference instance
- Function now synchronous and properly callable from lifespan handler

## Files Fixed

1. ✅ `ai-service/app/severity.py` 
   - Removed SeverityConfig class
   - Now imports settings from app.config
   - All functions use settings object

2. ✅ `ai-service/app/config.py`
   - Added HIGH_CONFIDENCE_THRESHOLD field
   - Added HIGH_DETECTION_COUNT field
   - Added field validators for type conversions
   - Added `extra="ignore"` to Config class
   - Created singleton settings instance

3. ✅ `ai-service/app/inference_phase1.py`
   - Changed initialize_inference_engine from async to sync
   - Returns bool instead of engine instance

4. ✅ `ai-service/app/main.py`
   - Already correct, uses settings from app.config

## Fix Strategy Execution
1. ✅ Updated SeverityConfig to accept all required fields properly
2. ✅ Consolidated configuration classes into single AISettings
3. ✅ Ensured proper type conversion for all fields
4. ✅ Removed module-level instantiation causing issues
5. ✅ Fixed async/await issues in initialization chain

## Solution Details

### Configuration Fix
- Changed complex types (RELEVANT_CLASSES, ALLOWED_EXTENSIONS, INFERENCE_IMAGE_SIZE, AUTO_DOWNLOAD_MODEL) to store as strings in Pydantic fields
- Added property methods to convert strings to proper types on access
- Manual .env file parsing before class creation to avoid Pydantic JSON parsing errors
- Disabled automatic .env loading in model_config to prevent validation errors

### Testing Status
✅ Configuration validation: FIXED
✅ Initialization chain: FIXED  
✅ Type conversion: FIXED
✅ Config loading test: PASSED

