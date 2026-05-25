# Demo & Testing Guide

Complete walkthrough for demonstrating the Online Attendance app and testing production-ready features.

---

## Prerequisites

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your Supabase URL and keys

# 3. Update Streamlit secrets
cat > .streamlit/secrets.toml << 'EOF'
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key"
EOF

# 4. Run database schema (ONE TIME in Supabase SQL Editor)
# Copy supabase_schema_v2.sql and paste into Supabase SQL Editor
```

---

## Demo Flow

### Part 1: Teacher Registration & Validation

**Goal**: Show input validation and error handling

```
1. Open app: streamlit run app.py
2. Click "Go to Teacher Portal"
3. Click "Register"

Test Case 1: Invalid Password
┌─────────────────────────────────────────┐
│ Registration Form                       │
├─────────────────────────────────────────┤
│ Username: john123                       │
│ Password: weak     [ENTER]              │
│ ❌ ERROR: "Password must be at least    │
│    8 characters"                        │
│                                         │
│ Password: Pass      [ENTER]             │
│ ❌ ERROR: "Password must contain at     │
│    least one digit"                     │
└─────────────────────────────────────────┘

Test Case 2: Valid Registration
│ Username: john.doe-123                  │
│ Password: SecurePass1                   │
│ Name: John Doe                          │
│ Confirm: SecurePass1                    │
│ ✅ "Teacher registered successfully!"   │
│                                         │
│ Check logs:                             │
│ tail -f .logs/attendance.log            │
│ → "AUTH_EVENT: teacher_register |      │
│    User: john.doe-123 | Status: SUCCESS"
└─────────────────────────────────────────┘
```

**Expected Outcomes**:
- ✅ Password validation enforced
- ✅ Clear error messages displayed
- ✅ Successful registration logged

---

### Part 2: Subject Creation

**Goal**: Show authorization and configuration

```
1. Click "Manage Subjects"
2. Click "Create Subject"

Form:
┌─────────────────────────────────────────┐
│ Create Subject                          │
├─────────────────────────────────────────┤
│ Subject Code: CS   [ENTER]              │
│ ❌ ERROR: "must be at least 3 characters"│
│                                         │
│ Subject Code: CS101                     │
│ Subject Name: Introduction to Computer |
│                Science                  │
│ Section: A                              │
│ ✅ "Subject created: CS101"             │
│                                         │
│ Check logs:                             │
│ → "DATA_ACCESS: create | Table: subjects│
│    | User: 1 | Record: 456"             │
└─────────────────────────────────────────┘

Expected in UI:
- Subject Code normalized to: CS101
- QR code generated with APP_DOMAIN
- Share link displayed
```

**Expected Outcomes**:
- ✅ Input validation applied
- ✅ Authorization verified (teacher owns subject)
- ✅ Audit logging recorded

---

### Part 3: Student Registration & Enrollment

**Goal**: Show face detection and error handling

```
1. Click "Go to Student Portal"
2. Take photo for face registration

Scenario A: Bad Image Quality
┌─────────────────────────────────────────┐
│ Take Attendance Photo                   │
│ [UPLOAD BLURRY IMAGE]                   │
│                                         │
│ ❌ ERROR: "No face detected in image.   │
│    Please use a clear, front-facing     │
│    photo with good lighting"            │
│                                         │
│ Check logs:                             │
│ → "ERROR_EVENT: ML_PIPELINE_FAILED |    │
│    Message: Face detection failed:      │
│    no faces found in image"             │
└─────────────────────────────────────────┘

Scenario B: Good Image
│ [UPLOAD CLEAR PHOTO]                    │
│ ✅ "Face registered successfully!"      │
│ Student created with ID: 123            │
│                                         │
│ Check logs:                             │
│ → "AUTH_EVENT: student_register |       │
│    ... | Status: SUCCESS"               │
└─────────────────────────────────────────┘

3. Enroll in Subject
│ Subject Code: CS101                     │
│ ✅ "Enrolled successfully!"             │
│                                         │
│ Dashboard shows:                        │
│ - CS101: 0/100 attended                 │
└─────────────────────────────────────────┘
```

**Expected Outcomes**:
- ✅ Face recognition error handling
- ✅ Friendly error messages (not stack traces)
- ✅ Audit trail for student registration
- ✅ Proper authorization (student can only enroll themselves)

---

### Part 4: Attendance Taking (Face Recognition)

**Goal**: Show ML error handling and data logging

```
1. Teacher: Click "Take Attendance"
2. Select Subject: CS101
3. Upload attendance photos

Scenario A: Corrupted Image
┌─────────────────────────────────────────┐
│ Upload Attendance Photos                │
│ [SELECT FILES WITH CORRUPTED IMAGES]    │
│                                         │
│ ❌ ERROR: "Could not process images.    │
│    Please ensure they are clear,        │
│    front-facing photos."                │
│                                         │
│ Check logs:                             │
│ → "ERROR_EVENT: ML_PIPELINE_FAILED"     │
└─────────────────────────────────────────┘

Scenario B: Valid Images
│ [SELECT VALID PHOTOS]                   │
│ ✅ "Attendance processed"               │
│ - John Doe: Present (confidence: 0.92)  │
│ - Jane Smith: Present (confidence: 0.88)│
│ - Bob Johnson: Absent                   │
│                                         │
│ Check logs:                             │
│ → "ATTENDANCE_EVENT: face_recognition   │
│    | Teacher: 1 | Subject: 101 |        │
│    Students: 3"                         │
└─────────────────────────────────────────┘

5. Review & Save
│ ✅ "Attendance saved: 2 present, 1 absent"│
│                                         │
│ Check logs:                             │
│ → "DATA_ACCESS: create | Table:         │
│    attendance_logs | User: 1 | Count: 3"│
└─────────────────────────────────────────┘
```

**Expected Outcomes**:
- ✅ ML pipeline errors handled gracefully
- ✅ Successful attendance recorded with confidence scores
- ✅ Audit trail for all operations
- ✅ Student dashboard updated

---

### Part 5: Authorization & Security Tests

**Goal**: Show that RLS and authorization work

```
Test A: Unauthorized Subject Access
┌─────────────────────────────────────────┐
│ Teacher A tries to modify Teacher B's   │
│ subject (should fail)                   │
│                                         │
│ ❌ ERROR: "You don't own this subject"  │
│                                         │
│ Check logs:                             │
│ → "WARNING: Unauthorized attendance     │
│    access: teacher 1 attempted to       │
│    access subject 999 (owned by 2)"     │
└─────────────────────────────────────────┘

Test B: Enrollment Verification
│ Student can only enroll in subjects     │
│ they have valid code for                │
│                                         │
│ Subject Code: INVALID                   │
│ ❌ ERROR: "Subject not found"           │
│                                         │
│ Student can only view their own records │
│ ✅ Dashboard shows only enrolled        │
│    subjects                             │
└─────────────────────────────────────────┘

Test C: Audit Trail
│ All operations logged:                  │
│ - Login attempts (success/failure)      │
│ - Data access (CRUD operations)         │
│ - Errors (with full context)            │
│                                         │
│ tail -f .logs/attendance.log:           │
│ 2024-05-20 13:48:10 - INFO - AUTH_EVENT│
│ 2024-05-20 13:48:15 - ERROR - ERROR_EVT│
│ 2024-05-20 13:48:20 - INFO - DATA_ACCS │
└─────────────────────────────────────────┘
```

**Expected Outcomes**:
- ✅ Authorization checks enforced
- ✅ Clear authorization error messages
- ✅ Complete audit trail available
- ✅ No sensitive data leaked in logs

---

## Performance Testing

### Memory Usage
```python
# Check session state size
import streamlit as st
import json

total_size = 0
for key, value in st.session_state.items():
    size = len(json.dumps(value, default=str))
    print(f"{key}: {size} bytes")
    total_size += size

print(f"Total session size: {total_size / 1024:.2f} KB")
# Expected: < 100 MB for normal usage
```

### Database Query Performance
```bash
# Monitor Supabase query times
# Check .logs/attendance.log for slow queries

# Example:
# 2024-05-20 13:48:10 - DEBUG - Query took 0.23s: get_teacher_subjects
# 2024-05-20 13:48:15 - WARNING - Query took 2.1s: get_all_students (slow!)
```

### Face Recognition Speed
```
# Expected times:
- Face detection: 0.5-1.5s per image
- Face embedding: 1-2s per face
- Classification: 0.2-0.5s
- Total per image: ~2-4s

# If slower, check:
- Image size (reduce if > 5MB)
- CPU available
- dlib version compatibility
```

---

## Logging Verification

### Check Logs
```bash
# View all logs
tail -f .logs/attendance.log

# Filter by event type
grep "AUTH_EVENT" .logs/attendance.log
grep "ERROR_EVENT" .logs/attendance.log
grep "DATA_ACCESS" .logs/attendance.log

# Check log rotation
ls -lh .logs/
# Expected: .log file + .log.1, .log.2 (rotated)
```

### Sample Log Output
```
2024-05-20 13:48:10,624 - attendance_app - INFO - Connecting to Supabase: https://...
2024-05-20 13:48:11,234 - attendance_app - INFO - Supabase client initialized successfully
2024-05-20 13:48:15,450 - attendance_app - INFO - AUTH_EVENT: teacher_login | User: john123 | Status: SUCCESS | teacher_id: 1
2024-05-20 13:48:20,123 - attendance_app - INFO - DATA_ACCESS: create | Table: subjects | User: 1 | Record: 456
2024-05-20 13:48:25,890 - attendance_app - ERROR - ERROR_EVENT: ML_PIPELINE_FAILED | Message: Face detection failed | User: 1
```

---

## Deployment Demo

### Docker Build & Run
```bash
# Build image
docker build -t attendance-app:demo .

# Run locally
docker run -p 8501:8501 \
  -e SUPABASE_URL="https://your-project.supabase.co" \
  -e SUPABASE_ANON_KEY="your-key" \
  -e APP_ENV="production" \
  attendance-app:demo

# Access: http://localhost:8501
```

### Health Check
```bash
# Check app health
curl http://localhost:8501/_stcore/health

# Expected response:
# {"status": "ok"}

# Check logs
docker logs <container-id>
```

---

## Demo Script (10-15 minutes)

```
[INTRO - 1 min]
"This is the Online Attendance app - an AI-powered classroom 
attendance system using face and voice recognition with proper 
security hardening and error handling."

[SECURITY FEATURES - 2 min]
1. Show README_SECURITY.md
   - Explain Anon key vs Service key
   - RLS policies
   - Authorization checks

[INPUT VALIDATION - 2 min]
1. Teacher registration
   - Show password requirements
   - Try weak password → error
   - Try strong password → success

[FACE RECOGNITION - 3 min]
1. Student registration with photo
2. Teacher uploads attendance photos
3. Show results with confidence scores
4. Show error handling with bad images

[LOGGING & AUDIT - 2 min]
1. Show .logs/attendance.log
   - Auth events
   - Data access
   - Errors

[DEPLOYMENT - 2 min]
1. Show docker-compose.yml
2. Explain multi-platform support
3. Show deployment guides

[Q&A - 2 min]
```

---

## Success Criteria

✅ **Demo Successful If:**
- All validations working correctly
- Error messages user-friendly
- Attendance processing works
- Logs contain proper audit trail
- No stack traces shown to users
- Performance acceptable
- Authorization enforced
- Authorization enforced

❌ **Demo Fails If:**
- App crashes on error
- Stack traces shown in UI
- Unauthorized access granted
- No logs generated
- Slow performance (<1s per operation)
- Validations bypassed

---

## Troubleshooting

### App Won't Start
```bash
# Check secrets
cat .streamlit/secrets.toml
# Should have SUPABASE_URL and SUPABASE_ANON_KEY

# Check logs
tail -f .logs/attendance.log
```

### Face Recognition Not Working
```
- Ensure camera/images are clear
- Try lowering FACE_DISTANCE_THRESHOLD in .env
- Check logs for ML errors
```

### No Logs Generated
```
- Check LOG_FILE in .env
- Ensure .logs directory exists and is writable
- Check LOG_LEVEL (set to DEBUG for verbose output)
```

### Performance Issues
```
- Check database queries: grep "query" .logs/attendance.log
- Reduce image sizes
- Check CPU/memory usage
- Enable caching for embeddings
```

---

## Next Steps

1. **Run local demo** (15 min)
   - Follow Demo Flow above
   - Record any issues

2. **Run test suite** (5 min)
   ```bash
   pytest test_errors_sample.py -v
   ```

3. **Deploy to platform** (varies)
   - Follow README_DEPLOYMENT.md
   - Run demo on production environment

4. **Gather feedback**
   - Security review
   - Performance review
   - User experience review
