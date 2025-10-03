## ✅ Added Sr. No. Column to Doctors Table

### **Changes Made:**

#### **1. Updated Table Header**
**Before:**
```html
<th>Name</th>
<th>Specialization</th>
<th>Experience</th>
<th>Status</th>
<th>Actions</th>
```

**After:**
```html
<th>Sr. No.</th>  <!-- NEW COLUMN -->
<th>Name</th>
<th>Specialization</th>
<th>Experience</th>
<th>Status</th>
<th>Actions</th>
```

#### **2. Updated Table Body**
**Before:**
```html
<tr v-for="doctor in filteredDoctors" :key="doctor.id">
    <td>Dr. {{ doctor.name }}</td>
    <td>{{ doctor.specialization }}</td>
    <td>{{ doctor.experience }} years</td>
```

**After:**
```html
<tr v-for="(doctor, index) in filteredDoctors" :key="doctor.id">
    <td>{{ index + 1 }}</td>  <!-- NEW SERIAL NUMBER -->
    <td>Dr. {{ doctor.name }}</td>
    <td>{{ doctor.specialization }}</td>
    <td>{{ doctor.experience }} years</td>
```

### **📋 Current Doctors Table Structure:**
1. **Sr. No.** - Sequential numbering (1, 2, 3, ...)
2. **Name** - Doctor name with "Dr." prefix
3. **Specialization** - Medical specialty
4. **Experience** - Years of experience
5. **Status** - Active/Inactive badge
6. **Actions** - Edit and Blacklist buttons

### **✅ Features:**
- **Auto-numbering**: Serial numbers update automatically as the list changes
- **Filter-aware**: Serial numbers adjust when doctors list is filtered
- **Consistent styling**: Matches the existing table design
- **Responsive**: Works on all screen sizes

### **🎯 Result:**
The doctors table now has a Sr. No. column as the first column, making it easier to reference specific doctors in the list.

**Test the change:** Login as admin → Go to Doctors tab → Verify Sr. No. column appears