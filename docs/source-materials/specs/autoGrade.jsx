import React, { useState, useEffect, createContext, useContext, useCallback } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, signInWithCustomToken, onAuthStateChanged } from 'firebase/auth';
import { getFirestore, collection, addDoc, getDocs, doc, updateDoc, deleteDoc, query, where, onSnapshot, setDoc, getDoc } from 'firebase/firestore';
import { getStorage, ref as storageRef, uploadBytesResumable, getDownloadURL, deleteObject } from 'firebase/storage';

// Define API key (empty string for Canvas runtime auto-provisioning)
const API_KEY = "";

// Create a context for Firebase services and user data
const FirebaseContext = createContext(null);

// Custom hook to use Firebase context
const useFirebase = () => {
  return useContext(FirebaseContext);
};

// --- Modern Icon Components ---
const ChevronLeftIcon = ({ className = "w-5 h-5" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
  </svg>
);

const PlusIcon = ({ className = "w-5 h-5" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
  </svg>
);

const SparklesIcon = ({ className = "w-4 h-4" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3l3.057-3L11 3l3.057 3.057L17 6l-2.943 2.943L11 12l-3.057-2.943L5 12l2.943-2.943L5 6V3z" />
  </svg>
);

const EditIcon = ({ className = "w-4 h-4" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
  </svg>
);

const TrashIcon = ({ className = "w-4 h-4" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
);

const FlagIcon = ({ className = "w-4 h-4" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 2H21l-3 6 3 6h-8.5l-1-2H5a2 2 0 00-2 2zm9-13.5V9" />
  </svg>
);

const EyeIcon = ({ className = "w-4 h-4" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
  </svg>
);

const SettingsIcon = ({ className = "w-4 h-4" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

const ReportIcon = ({ className = "w-4 h-4" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
);

// --- Modern Loading Component ---
const LoadingSpinner = ({ size = "md" }) => {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6", 
    lg: "w-8 h-8"
  };
  
  return (
    <div className={`animate-spin rounded-full border-2 border-slate-200 border-t-blue-500 ${sizeClasses[size]}`}></div>
  );
};

// --- Modern Progress Bar ---
const ProgressBar = ({ progress, className = "" }) => (
  <div className={`w-full bg-slate-200 rounded-full h-2 overflow-hidden ${className}`}>
    <div 
      className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full transition-all duration-300 ease-out"
      style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
    />
  </div>
);

// --- Modern Button Component ---
const Button = ({ 
  variant = "primary", 
  size = "md", 
  children, 
  disabled = false, 
  loading = false, 
  icon: Icon,
  className = "",
  ...props 
}) => {
  const baseClasses = "inline-flex items-center justify-center font-medium rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";
  
  const variants = {
    primary: "bg-blue-600 hover:bg-blue-700 text-white shadow-sm hover:shadow-md focus:ring-blue-500",
    secondary: "bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 shadow-sm hover:shadow-md focus:ring-slate-500",
    success: "bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm hover:shadow-md focus:ring-emerald-500",
    warning: "bg-amber-500 hover:bg-amber-600 text-white shadow-sm hover:shadow-md focus:ring-amber-500",
    danger: "bg-red-500 hover:bg-red-600 text-white shadow-sm hover:shadow-md focus:ring-red-500",
    ghost: "bg-transparent hover:bg-slate-100 text-slate-700 focus:ring-slate-500",
    ai: "bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white shadow-sm hover:shadow-md focus:ring-purple-500"
  };
  
  const sizes = {
    sm: "px-3 py-2 text-sm",
    md: "px-4 py-2.5 text-sm",
    lg: "px-6 py-3 text-base"
  };
  
  return (
    <button
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <LoadingSpinner size="sm" />
      ) : (
        <>
          {Icon && <Icon className="w-4 h-4 mr-2" />}
          {children}
        </>
      )}
    </button>
  );
};

// --- Modern Card Component ---
const Card = ({ children, className = "", hover = true }) => (
  <div className={`bg-white rounded-2xl shadow-sm border border-slate-200 ${hover ? 'hover:shadow-md transition-shadow duration-200' : ''} ${className}`}>
    {children}
  </div>
);

const CardHeader = ({ children, className = "" }) => (
  <div className={`px-6 py-4 border-b border-slate-200 ${className}`}>
    {children}
  </div>
);

const CardContent = ({ children, className = "" }) => (
  <div className={`px-6 py-4 ${className}`}>
    {children}
  </div>
);

// --- Modern Modal Component ---
const Modal = ({ isOpen, onClose, title, size = "md", children }) => {
  const sizeClasses = {
    sm: "max-w-md",
    md: "max-w-2xl",
    lg: "max-w-4xl",
    xl: "max-w-6xl"
  };
  
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity" 
          onClick={onClose}
        />
        <div className={`relative w-full ${sizeClasses[size]} bg-white rounded-2xl shadow-xl transform transition-all`}>
          <div className="flex items-center justify-between p-6 border-b border-slate-200">
            <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-600 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="p-6 max-h-[calc(100vh-200px)] overflow-y-auto">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

// --- Modern Input Component ---
const Input = ({ label, error, className = "", ...props }) => (
  <div className={className}>
    {label && (
      <label className="block text-sm font-medium text-slate-700 mb-2">
        {label}
      </label>
    )}
    <input
      className={`w-full px-4 py-2.5 rounded-xl border ${
        error ? 'border-red-300 focus:border-red-500' : 'border-slate-300 focus:border-blue-500'
      } focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors`}
      {...props}
    />
    {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
  </div>
);

const TextArea = ({ label, error, className = "", ...props }) => (
  <div className={className}>
    {label && (
      <label className="block text-sm font-medium text-slate-700 mb-2">
        {label}
      </label>
    )}
    <textarea
      className={`w-full px-4 py-2.5 rounded-xl border ${
        error ? 'border-red-300 focus:border-red-500' : 'border-slate-300 focus:border-blue-500'
      } focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors resize-y`}
      {...props}
    />
    {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
  </div>
);

const Select = ({ label, error, className = "", children, ...props }) => (
  <div className={className}>
    {label && (
      <label className="block text-sm font-medium text-slate-700 mb-2">
        {label}
      </label>
    )}
    <select
      className={`w-full px-4 py-2.5 rounded-xl border ${
        error ? 'border-red-300 focus:border-red-500' : 'border-slate-300 focus:border-blue-500'
      } focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors bg-white`}
      {...props}
    >
      {children}
    </select>
    {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
  </div>
);

// --- Modern Alert Component ---
const Alert = ({ type = "info", title, children, className = "" }) => {
  const types = {
    info: "bg-blue-50 border-blue-200 text-blue-800",
    success: "bg-emerald-50 border-emerald-200 text-emerald-800", 
    warning: "bg-amber-50 border-amber-200 text-amber-800",
    error: "bg-red-50 border-red-200 text-red-800"
  };
  
  return (
    <div className={`rounded-xl border p-4 ${types[type]} ${className}`}>
      {title && <h4 className="font-medium mb-2">{title}</h4>}
      {children}
    </div>
  );
};

// --- Modern Toast Notification ---
const Toast = ({ message, type = "info", onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 5000);
    return () => clearTimeout(timer);
  }, [onClose]);
  
  const types = {
    info: "bg-blue-600",
    success: "bg-emerald-600",
    warning: "bg-amber-600", 
    error: "bg-red-600"
  };
  
  return (
    <div className={`fixed top-4 right-4 z-50 ${types[type]} text-white px-6 py-4 rounded-xl shadow-lg transform transition-all duration-300`}>
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">{message}</span>
        <button onClick={onClose} className="ml-4 text-white/80 hover:text-white">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
};

// --- File Upload Utility ---
const uploadFileToFirebase = async (file, storage, path, setUploadProgress, showToast) => {
  if (!file || !storage) {
    showToast?.('No file selected for upload or storage not ready.', 'error');
    return null;
  }

  return new Promise((resolve) => {
    const filePath = `${path}${file.name}_${new Date().getTime()}`;
    const fileRef = storageRef(storage, filePath);
    const uploadTask = uploadBytesResumable(fileRef, file);

    uploadTask.on(
      'state_changed',
      (snapshot) => {
        const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
        setUploadProgress?.(progress);
      },
      (error) => {
        console.error("Upload failed:", error);
        showToast?.(`File upload failed: ${error.message}`, 'error');
        resolve(null);
      },
      async () => {
        try {
          const downloadURL = await getDownloadURL(uploadTask.snapshot.ref);
          showToast?.('File uploaded successfully!', 'success');
          resolve(downloadURL);
        } catch (error) {
          console.error("Error getting download URL:", error);
          showToast?.(`Error getting file URL: ${error.message}`, 'error');
          resolve(null);
        }
      }
    );
  });
};

const deleteFileFromFirebase = async (fileUrl, storage, showToast) => {
  if (!fileUrl || !storage) return false;
  
  try {
    const fileRef = storageRef(storage, fileUrl);
    await deleteObject(fileRef);
    showToast?.('File deleted successfully.', 'success');
    return true;
  } catch (error) {
    console.error("Error deleting file:", error);
    showToast?.(`Error deleting file: ${error.message}`, 'error');
    return false;
  }
};

// --- AI Consent Modal ---
const AIConsentModal = ({ onAccept }) => (
  <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
    <div className="bg-white rounded-2xl p-8 shadow-2xl max-w-md w-full">
      <div className="text-center mb-6">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <SparklesIcon className="w-8 h-8 text-blue-600" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">AI Feature Consent</h2>
        <p className="text-slate-600 leading-relaxed">
          To improve our AI-powered features like feedback generation and content suggestions, we need your consent to use anonymized data from your interactions.
        </p>
      </div>
      
      <div className="space-y-3 mb-6 text-sm text-slate-600">
        <div className="flex items-start space-x-3">
          <div className="w-2 h-2 bg-emerald-500 rounded-full mt-2 flex-shrink-0" />
          <span>Your data is always anonymized; personal information is never used for AI training.</span>
        </div>
        <div className="flex items-start space-x-3">
          <div className="w-2 h-2 bg-emerald-500 rounded-full mt-2 flex-shrink-0" />
          <span>This helps us understand which suggestions are helpful and which are not.</span>
        </div>
        <div className="flex items-start space-x-3">
          <div className="w-2 h-2 bg-emerald-500 rounded-full mt-2 flex-shrink-0" />
          <span>You are always in control and can flag any inaccurate AI suggestions.</span>
        </div>
      </div>
      
      <Button variant="primary" size="lg" className="w-full" onClick={onAccept}>
        Accept and Continue
      </Button>
    </div>
  </div>
);

// --- Course Management Components ---
const CourseForm = ({ onSave, onCancel, initialCourseData = null }) => {
  const [courseName, setCourseName] = useState(initialCourseData?.name || '');
  const [description, setDescription] = useState(initialCourseData?.description || '');
  const [errors, setErrors] = useState({});

  const handleSubmit = (e) => {
    e.preventDefault();
    const newErrors = {};
    
    if (!courseName.trim()) {
      newErrors.courseName = 'Course name is required';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    
    onSave({ name: courseName, description });
  };

  return (
    <Modal 
      isOpen={true} 
      onClose={onCancel}
      title={initialCourseData ? 'Edit Course' : 'Add New Course'}
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        <Input
          label="Course Name *"
          value={courseName}
          onChange={(e) => {
            setCourseName(e.target.value);
            if (errors.courseName) setErrors(prev => ({ ...prev, courseName: '' }));
          }}
          placeholder="e.g., Composition I"
          error={errors.courseName}
        />
        
        <TextArea
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Brief description of the course..."
          rows={4}
        />
        
        <div className="flex justify-end space-x-3">
          <Button variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit" variant="primary">
            {initialCourseData ? 'Save Changes' : 'Add Course'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

// --- Course List Component ---
const CourseList = ({ onSelectCourse }) => {
  const { db, userId, isAuthReady } = useFirebase();
  const [courses, setCourses] = useState([]);
  const [showAddCourseForm, setShowAddCourseForm] = useState(false);
  const [editingCourse, setEditingCourse] = useState(null);
  const [courseToDelete, setCourseToDelete] = useState(null);
  const [toast, setToast] = useState(null);
  const [loading, setLoading] = useState(true);

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
  };

  const defaultCourses = [
    { name: 'Composition 1', description: 'Fundamental principles of academic writing and rhetoric.' },
    { name: 'Composition 2', description: 'Advanced research, argumentation, and literary analysis.' },
  ];

  const addDefaultCoursesToDb = useCallback(async () => {
    if (!db || !userId) return;
    
    const coursesCollectionRef = collection(db, `artifacts/${__app_id}/users/${userId}/courses`);
    const existingCoursesSnapshot = await getDocs(coursesCollectionRef);
    
    if (existingCoursesSnapshot.empty) {
      for (const course of defaultCourses) {
        try {
          await addDoc(coursesCollectionRef, course);
        } catch (e) {
          console.error("Error adding default course:", e);
        }
      }
      showToast('Default courses added!', 'success');
    }
  }, [db, userId]);

  useEffect(() => {
    if (!isAuthReady || !db || !userId) return;

    const coursesCollectionRef = collection(db, `artifacts/${__app_id}/users/${userId}/courses`);
    
    const unsubscribe = onSnapshot(coursesCollectionRef, (snapshot) => {
      const coursesData = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setCourses(coursesData);
      setLoading(false);

      if (coursesData.length === 0) {
        addDefaultCoursesToDb();
      }
    }, (error) => {
      console.error("Error fetching courses:", error);
      showToast('Failed to load courses', 'error');
      setLoading(false);
    });

    return () => unsubscribe();
  }, [db, userId, isAuthReady, addDefaultCoursesToDb]);

  const handleAddCourse = async (courseData) => {
    if (!db || !userId) return;
    
    try {
      await addDoc(collection(db, `artifacts/${__app_id}/users/${userId}/courses`), courseData);
      showToast('Course added successfully!', 'success');
      setShowAddCourseForm(false);
    } catch (e) {
      console.error("Error adding course:", e);
      showToast('Error adding course', 'error');
    }
  };

  const handleUpdateCourse = async (courseData) => {
    if (!db || !userId || !editingCourse) return;
    
    try {
      const courseRef = doc(db, `artifacts/${__app_id}/users/${userId}/courses`, editingCourse.id);
      await updateDoc(courseRef, courseData);
      showToast('Course updated successfully!', 'success');
      setEditingCourse(null);
    } catch (e) {
      console.error("Error updating course:", e);
      showToast('Error updating course', 'error');
    }
  };

  const handleDeleteCourse = async () => {
    if (!db || !userId || !courseToDelete) return;
    
    try {
      const courseRef = doc(db, `artifacts/${__app_id}/users/${userId}/courses`, courseToDelete.id);
      await deleteDoc(courseRef);
      showToast('Course deleted successfully!', 'success');
    } catch (e) {
      console.error("Error deleting course:", e);
      showToast('Error deleting course', 'error');
    } finally {
      setCourseToDelete(null);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-slate-600">Loading your courses...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-8">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-slate-900 mb-4">Your Courses</h1>
        <p className="text-slate-600 text-lg">Manage your courses, assignments, and student feedback</p>
      </div>

      <div className="flex justify-center mb-8">
        <Button 
          variant="primary" 
          size="lg" 
          icon={PlusIcon}
          onClick={() => setShowAddCourseForm(true)}
        >
          Add New Course
        </Button>
      </div>

      {courses.length === 0 ? (
        <div className="text-center py-16">
          <div className="w-24 h-24 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-12 h-12 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-slate-900 mb-2">No courses yet</h3>
          <p className="text-slate-600 mb-6">Create your first course to get started with managing assignments and student feedback.</p>
          <Button variant="primary" icon={PlusIcon} onClick={() => setShowAddCourseForm(true)}>
            Create Your First Course
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map(course => (
            <Card key={course.id} className="flex flex-col">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-slate-900">{course.name}</h3>
                  <div className="flex space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={EditIcon}
                      onClick={() => setEditingCourse(course)}
                      aria-label={`Edit ${course.name}`}
                    />
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={TrashIcon}
                      onClick={() => setCourseToDelete(course)}
                      aria-label={`Delete ${course.name}`}
                    />
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={EyeIcon}
                      onClick={() => onSelectCourse(course)}
                      aria-label={`View ${course.name}`}
                    />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600 line-clamp-3">{course.description || 'No description provided'}</p>
                <Button
                  variant="primary"
                  size="sm"
                  className="mt-4 w-full"
                  onClick={() => onSelectCourse(course)}
                >
                  View Course
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {showAddCourseForm && (
        <CourseForm
          onSave={handleAddCourse}
          onCancel={() => setShowAddCourseForm(false)}
        />
      )}

      {editingCourse && (
        <CourseForm
          initialCourseData={editingCourse}
          onSave={handleUpdateCourse}
          onCancel={() => setEditingCourse(null)}
        />
      )}

      {courseToDelete && (
        <Modal
          isOpen={true}
          onClose={() => setCourseToDelete(null)}
          title="Confirm Delete"
          size="sm"
        >
          <div className="space-y-6">
            <p className="text-slate-600">
              Are you sure you want to delete the course <span className="font-semibold">{courseToDelete.name}</span>? This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-3">
              <Button variant="secondary" onClick={() => setCourseToDelete(null)}>
                Cancel
              </Button>
              <Button variant="danger" onClick={handleDeleteCourse}>
                Delete Course
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
};

// --- Assignment Management Components ---
const AssignmentForm = ({ courseId, onSave, onCancel, initialAssignmentData = null }) => {
  const { db, userId, storage, showToast } = useFirebase();
  const [title, setTitle] = useState(initialAssignmentData?.title || '');
  const [description, setDescription] = useState(initialAssignmentData?.description || '');
  const [dueDate, setDueDate] = useState(initialAssignmentData?.dueDate || '');
  const [file, setFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errors, setErrors] = useState({});

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newErrors = {};

    if (!title.trim()) {
      newErrors.title = 'Assignment title is required';
    }
    if (!dueDate) {
      newErrors.dueDate = 'Due date is required';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    let fileUrl = initialAssignmentData?.fileUrl || null;
    if (file) {
      fileUrl = await uploadFileToFirebase(
        file,
        storage,
        `artifacts/${__app_id}/users/${userId}/courses/${courseId}/assignments/`,
        setUploadProgress,
        showToast
      );
      if (!fileUrl) {
        showToast('Failed to upload file', 'error');
        return;
      }
    }

    onSave({
      title,
      description,
      dueDate,
      fileUrl,
      createdAt: initialAssignmentData?.createdAt || new Date().toISOString(),
    });
  };

  return (
    <Modal
      isOpen={true}
      onClose={onCancel}
      title={initialAssignmentData ? 'Edit Assignment' : 'Add New Assignment'}
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        <Input
          label="Assignment Title *"
          value={title}
          onChange={(e) => {
            setTitle(e.target.value);
            if (errors.title) setErrors((prev) => ({ ...prev, title: '' }));
          }}
          placeholder="e.g., Essay #1: Argumentative Writing"
          error={errors.title}
        />

        <TextArea
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Brief description of the assignment..."
          rows={4}
        />

        <Input
          label="Due Date *"
          type="date"
          value={dueDate}
          onChange={(e) => {
            setDueDate(e.target.value);
            if (errors.dueDate) setErrors((prev) => ({ ...prev, dueDate: '' }));
          }}
          error={errors.dueDate}
        />

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Upload File (Optional)
          </label>
          <input
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
            className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-colors"
          />
          {uploadProgress > 0 && uploadProgress < 100 && (
            <ProgressBar progress={uploadProgress} className="mt-2" />
          )}
        </div>

        <div className="flex justify-end space-x-3">
          <Button variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" loading={uploadProgress > 0 && uploadProgress < 100}>
            {initialAssignmentData ? 'Save Changes' : 'Add Assignment'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

const AssignmentList = ({ courseId, courseName }) => {
  const { db, userId, storage, showToast } = useFirebase();
  const [assignments, setAssignments] = useState([]);
  const [showAddAssignmentForm, setShowAddAssignmentForm] = useState(false);
  const [editingAssignment, setEditingAssignment] = useState(null);
  const [assignmentToDelete, setAssignmentToDelete] = useState(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    if (!db || !userId || !courseId) return;

    const assignmentsCollectionRef = collection(
      db,
      `artifacts/${__app_id}/users/${userId}/courses/${courseId}/assignments`
    );

    const unsubscribe = onSnapshot(assignmentsCollectionRef, (snapshot) => {
      const assignmentsData = snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
      setAssignments(assignmentsData);
      setLoading(false);
    }, (error) => {
      console.error("Error fetching assignments:", error);
      showToast('Failed to load assignments', 'error');
      setLoading(false);
    });

    return () => unsubscribe();
  }, [db, userId, courseId, showToast]);

  const handleAddAssignment = async (assignmentData) => {
    if (!db || !userId || !courseId) return;

    try {
      await addDoc(
        collection(db, `artifacts/${__app_id}/users/${userId}/courses/${courseId}/assignments`),
        assignmentData
      );
      showToast('Assignment added successfully!', 'success');
      setShowAddAssignmentForm(false);
    } catch (e) {
      console.error("Error adding assignment:", e);
      showToast('Error adding assignment', 'error');
    }
  };

  const handleUpdateAssignment = async (assignmentData) => {
    if (!db || !userId || !courseId || !editingAssignment) return;

    try {
      const assignmentRef = doc(
        db,
        `artifacts/${__app_id}/users/${userId}/courses/${courseId}/assignments`,
        editingAssignment.id
      );
      await updateDoc(assignmentRef, assignmentData);
      showToast('Assignment updated successfully!', 'success');
      setEditingAssignment(null);
    } catch (e) {
      console.error("Error updating assignment:", e);
      showToast('Error updating assignment', 'error');
    }
  };

  const handleDeleteAssignment = async () => {
    if (!db || !userId || !courseId || !assignmentToDelete) return;

    try {
      if (assignmentToDelete.fileUrl) {
        await deleteFileFromFirebase(assignmentToDelete.fileUrl, storage, showToast);
      }
      const assignmentRef = doc(
        db,
        `artifacts/${__app_id}/users/${userId}/courses/${courseId}/assignments`,
        assignmentToDelete.id
      );
      await deleteDoc(assignmentRef);
      showToast('Assignment deleted successfully!', 'success');
    } catch (e) {
      console.error("Error deleting assignment:", e);
      showToast('Error deleting assignment', 'error');
    } finally {
      setAssignmentToDelete(null);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-slate-600">Loading assignments...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center mb-8">
        <Button
          variant="ghost"
          icon={ChevronLeftIcon}
          onClick={() => window.history.back()}
          className="mr-4"
        >
          Back to Courses
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-slate-900">{courseName}</h1>
          <p className="text-slate-600">Manage assignments for this course</p>
        </div>
      </div>

      <div className="flex justify-center mb-8">
        <Button
          variant="primary"
          size="lg"
          icon={PlusIcon}
          onClick={() => setShowAddAssignmentForm(true)}
        >
          Add New Assignment
        </Button>
      </div>

      {assignments.length === 0 ? (
        <div className="text-center py-16">
          <div className="w-24 h-24 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-12 h-12 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-slate-900 mb-2">No assignments yet</h3>
          <p className="text-slate-600 mb-6">Create your first assignment for this course.</p>
          <Button
            variant="primary"
            icon={PlusIcon}
            onClick={() => setShowAddAssignmentForm(true)}
          >
            Create Your First Assignment
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {assignments.map((assignment) => (
            <Card key={assignment.id} className="flex flex-col">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-slate-900">{assignment.title}</h3>
                  <div className="flex space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={EditIcon}
                      onClick={() => setEditingAssignment(assignment)}
                      aria-label={`Edit ${assignment.title}`}
                    />
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={TrashIcon}
                      onClick={() => setAssignmentToDelete(assignment)}
                      aria-label={`Delete ${assignment.title}`}
                    />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600 line-clamp-3">{assignment.description || 'No description provided'}</p>
                <p className="text-sm text-slate-500 mt-2">
                  Due: {new Date(assignment.dueDate).toLocaleDateString()}
                </p>
                {assignment.fileUrl && (
                  <a
                    href={assignment.fileUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:underline mt-2 block"
                  >
                    View Attached File
                  </a>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {showAddAssignmentForm && (
        <AssignmentForm
          courseId={courseId}
          onSave={handleAddAssignment}
          onCancel={() => setShowAddAssignmentForm(false)}
        />
      )}

      {editingAssignment && (
        <AssignmentForm
          courseId={courseId}
          initialAssignmentData={editingAssignment}
          onSave={handleUpdateAssignment}
          onCancel={() => setEditingAssignment(null)}
        />
      )}

      {assignmentToDelete && (
        <Modal
          isOpen={true}
          onClose={() => setAssignmentToDelete(null)}
          title="Confirm Delete"
          size="sm"
        >
          <div className="space-y-6">
            <p className="text-slate-600">
              Are you sure you want to delete the assignment{' '}
              <span className="font-semibold">{assignmentToDelete.title}</span>? This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-3">
              <Button variant="secondary" onClick={() => setAssignmentToDelete(null)}>
                Cancel
              </Button>
              <Button variant="danger" onClick={handleDeleteAssignment}>
                Delete Assignment
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
};

// --- Firebase Provider Component ---
const FirebaseProvider = ({ children }) => {
  const [app, setApp] = useState(null);
  const [auth, setAuth] = useState(null);
  const [db, setDb] = useState(null);
  const [storage, setStorage] = useState(null);
  const [userId, setUserId] = useState(null);
  const [isAuthReady, setIsAuthReady] = useState(false);
  const [showAIConsent, setShowAIConsent] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = useCallback((message, type = 'info') => {
    setToast({ message, type });
  }, []);

  useEffect(() => {
    const firebaseConfig = {
      apiKey: API_KEY || process.env.REACT_APP_FIREBASE_API_KEY,
      authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
      projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
      storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
      messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
      appId: process.env.REACT_APP_FIREBASE_APP_ID,
    };

    const initializeFirebase = async () => {
      try {
        const firebaseApp = initializeApp(firebaseConfig);
        const authInstance = getAuth(firebaseApp);
        const dbInstance = getFirestore(firebaseApp);
        const storageInstance = getStorage(firebaseApp);

        setApp(firebaseApp);
        setAuth(authInstance);
        setDb(dbInstance);
        setStorage(storageInstance);

        onAuthStateChanged(authInstance, async (user) => {
          if (user) {
            setUserId(user.uid);
            const consentRef = doc(dbInstance, `artifacts/${__app_id}/users/${user.uid}/settings`, 'aiConsent');
            const consentDoc = await getDoc(consentRef);
            setShowAIConsent(!consentDoc.exists() || !consentDoc.data()?.accepted);
          } else {
            try {
              const result = await signInAnonymously(authInstance);
              setUserId(result.user.uid);
              const consentRef = doc(dbInstance, `artifacts/${__app_id}/users/${result.user.uid}/settings`, 'aiConsent');
              const consentDoc = await getDoc(consentRef);
              setShowAIConsent(!consentDoc.exists() || !consentDoc.data()?.accepted);
            } catch (error) {
              console.error("Error signing in anonymously:", error);
              showToast('Failed to authenticate user', 'error');
            }
          }
          setIsAuthReady(true);
        });
      } catch (error) {
        console.error("Error initializing Firebase:", error);
        showToast('Failed to initialize Firebase', 'error');
        setIsAuthReady(true);
      }
    };

    initializeFirebase();
  }, [showToast]);

  const handleAIConsent = async () => {
    if (!db || !userId) return;

    try {
      const consentRef = doc(db, `artifacts/${__app_id}/users/${userId}/settings`, 'aiConsent');
      await setDoc(consentRef, { accepted: true, timestamp: new Date().toISOString() });
      setShowAIConsent(false);
      showToast('Thank you for enabling AI features!', 'success');
    } catch (error) {
      console.error("Error saving AI consent:", error);
      showToast('Failed to save AI consent', 'error');
    }
  };

  return (
    <FirebaseContext.Provider
      value={{
        app,
        auth,
        db,
        storage,
        userId,
        isAuthReady,
        showToast,
      }}
    >
      {showAIConsent && <AIConsentModal onAccept={handleAIConsent} />}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
      {children}
    </FirebaseContext.Provider>
  );
};

// --- Main App Component ---
const App = () => {
  const [selectedCourse, setSelectedCourse] = useState(null);

  return (
    <FirebaseProvider>
      <div className="min-h-screen bg-slate-50">
        {selectedCourse ? (
          <AssignmentList
            courseId={selectedCourse.id}
            courseName={selectedCourse.name}
          />
        ) : (
          <CourseList onSelectCourse={setSelectedCourse} />
        )}
      </div>
    </FirebaseProvider>
  );
};

export default App;