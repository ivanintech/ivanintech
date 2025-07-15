'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AnimatedSection } from '@/components/ui/animated-section';
import { FaBrain, FaGraduationCap, FaCode, FaExternalLinkAlt, FaStar, FaRobot, FaChartLine, FaEye, FaBuilding, FaVrCardboard, FaServer, FaDesktop, FaReact, FaPython, FaJava, FaDocker, FaGitAlt, FaGithub, FaDatabase, FaPlus, FaEdit, FaTrash } from 'react-icons/fa';
import { SiNextdotjs, SiFastapi, SiPostgresql, SiTensorflow, SiPytorch, SiScikitlearn, SiOpencv, SiPandas, SiNumpy, SiSharp, SiUnity, SiFlask, SiGooglegemini } from 'react-icons/si';
import { useAuth } from '@/context/AuthContext';
import ProjectModal from '@/components/admin/ProjectModal';
import { ProjectCard } from '@/components/portfolio/project-card';
import apiClient from '@/lib/api-client';
import type { Project } from '@/types';

// Define the paginated response structure matching the backend
interface PaginatedProjectsResponse {
  items: DynamicProject[];
  total: number;
  page: number;
  per_page: number;
}

// Types
type ProjectCategory = 'ai-ml' | 'full-stack' | 'game-dev' | 'health-tech' | 'enterprise' | 'all';

interface Technology {
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}

interface CompanyProject {
  id: string;
  title: string;
  description: string;
  longDescription: string;
  technologies: Technology[];
  projectUrl?: string;
  imageUrl?: string;
  role: string;
  achievements: string[];
  sector: string;
  yearDeveloped: number;
}

interface DynamicProject {
  id: string;
  title: string;
  description: string;
  is_featured?: boolean;
  videoUrl?: string;
  imageUrl?: string;
  technologies?: Technology[] | string[] | { name: string }[];
  github_url?: string;
  githubUrl?: string;
  live_url?: string;
  category?: ProjectCategory;
  yearDeveloped?: number;
  aiPowered?: boolean;
  grade?: string;
  achievements?: string[];
  academicProject?: boolean;
}

interface PortfolioProject {
  id: string;
  title: string;
  description: string;
  longDescription: string;
  category: ProjectCategory;
  technologies: Technology[];
  githubUrl?: string;
  liveUrl?: string;
  featured: boolean;
  aiPowered: boolean;
  academicProject: boolean;
  grade?: string;
  complexity: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  achievements: string[];
  yearDeveloped: number;
  imageUrl?: string;
  videoUrl?: string;
}

// Technologies Available
const technologies: Record<string, Technology> = {
  // Core Programming Languages
  python: { name: 'Python', icon: FaPython, color: 'bg-blue-600 text-white' },
  c: { name: 'C', icon: FaCode, color: 'bg-blue-800 text-white' },
  csharp: { name: 'C#', icon: SiSharp, color: 'bg-purple-600 text-white' },
  java: { name: 'Java', icon: FaJava, color: 'bg-orange-600 text-white' },

  // AI/ML Frameworks & Libraries
  tensorflow: { name: 'TensorFlow', icon: SiTensorflow, color: 'bg-orange-600 text-white' },
  pytorch: { name: 'PyTorch', icon: SiPytorch, color: 'bg-red-600 text-white' },
  scikitlearn: { name: 'Scikit-learn', icon: SiScikitlearn, color: 'bg-orange-500 text-white' },
  huggingface: { name: 'Hugging Face', icon: FaRobot, color: 'bg-yellow-600 text-white' },
  transformers: { name: 'Transformers', icon: FaBrain, color: 'bg-purple-700 text-white' },
  langchain: { name: 'LangChain', icon: FaRobot, color: 'bg-green-700 text-white' },
  ollama: { name: 'Ollama', icon: FaServer, color: 'bg-gray-800 text-white' },
  gradio: { name: 'Gradio', icon: FaDesktop, color: 'bg-orange-600 text-white' },
  
  // Generative AI & LLMs
  gemini: { name: 'Gemini AI', icon: SiGooglegemini, color: 'bg-purple-600 text-white' },
  chatgpt: { name: 'ChatGPT', icon: FaRobot, color: 'bg-green-600 text-white' },
  llm: { name: 'Large Language Models', icon: FaBrain, color: 'bg-indigo-600 text-white' },
  genai: { name: 'Generative AI', icon: FaRobot, color: 'bg-pink-600 text-white' },
  
  // Data Science & Analysis
  pandas: { name: 'Pandas', icon: SiPandas, color: 'bg-blue-800 text-white' },
  numpy: { name: 'NumPy', icon: SiNumpy, color: 'bg-blue-600 text-white' },
  matplotlib: { name: 'Matplotlib', icon: FaChartLine, color: 'bg-blue-700 text-white' },
  seaborn: { name: 'Seaborn', icon: FaChartLine, color: 'bg-teal-600 text-white' },
  plotly: { name: 'Plotly', icon: FaChartLine, color: 'bg-purple-600 text-white' },
  
  // Computer Vision
  opencv: { name: 'OpenCV', icon: SiOpencv, color: 'bg-green-600 text-white' },
  pil: { name: 'PIL/Pillow', icon: FaEye, color: 'bg-yellow-600 text-white' },
  yolo: { name: 'YOLO', icon: FaEye, color: 'bg-red-600 text-white' },
  
  // Planning & Reasoning
  pddl: { name: 'PDDL', icon: FaBrain, color: 'bg-purple-800 text-white' },
  prolog: { name: 'Prolog', icon: FaBrain, color: 'bg-red-700 text-white' },
  asp: { name: 'Answer Set Programming', icon: FaBrain, color: 'bg-gray-700 text-white' },
  
  // Web Development
  nextjs: { name: 'Next.js', icon: SiNextdotjs, color: 'bg-black text-white' },
  react: { name: 'React', icon: FaReact, color: 'bg-blue-500 text-white' },
  fastapi: { name: 'FastAPI', icon: SiFastapi, color: 'bg-green-600 text-white' },
  flask: { name: 'Flask', icon: SiFlask, color: 'bg-gray-800 text-white' },
  
  // Databases
  postgresql: { name: 'PostgreSQL', icon: SiPostgresql, color: 'bg-blue-800 text-white' },
  redis: { name: 'Redis', icon: FaDatabase, color: 'bg-red-600 text-white' },
  
  // Cloud & DevOps
  docker: { name: 'Docker', icon: FaDocker, color: 'bg-blue-500 text-white' },
  aws: { name: 'AWS', icon: FaServer, color: 'bg-orange-600 text-white' },
  gcp: { name: 'Google Cloud', icon: FaServer, color: 'bg-blue-600 text-white' },
  
  // Game Development & 3D
  unity: { name: 'Unity', icon: SiUnity, color: 'bg-black text-white' },
  
  // Tools & Version Control
  git: { name: 'Git', icon: FaGitAlt, color: 'bg-orange-600 text-white' },
  github: { name: 'GitHub', icon: FaGithub, color: 'bg-gray-800 text-white' },
  jupyter: { name: 'Jupyter', icon: SiFlask, color: 'bg-orange-600 text-white' },
  colab: { name: 'Google Colab', icon: FaCode, color: 'bg-yellow-600 text-white' },
  
  // MLOps & Deployment
  mlflow: { name: 'MLflow', icon: FaServer, color: 'bg-blue-700 text-white' },
  kubeflow: { name: 'Kubeflow', icon: FaServer, color: 'bg-blue-800 text-white' },
  streamlit: { name: 'Streamlit', icon: FaDesktop, color: 'bg-red-600 text-white' },
  
  // AutoML & No-Code
  automl: { name: 'AutoML', icon: FaRobot, color: 'bg-purple-700 text-white' },
  optuna: { name: 'Optuna', icon: FaChartLine, color: 'bg-blue-700 text-white' },
  
  // Search & Retrieval
  faiss: { name: 'FAISS', icon: FaDatabase, color: 'bg-indigo-600 text-white' },
  elasticsearch: { name: 'Elasticsearch', icon: FaDatabase, color: 'bg-yellow-600 text-white' },
  
  // Cognitive & Neuroscience
  neuroscience: { name: 'Neuroscience', icon: FaBrain, color: 'bg-pink-700 text-white' },
  cognitive: { name: 'Cognitive Systems', icon: FaBrain, color: 'bg-indigo-700 text-white' },
  
  // VR/AR
  ar: { name: 'Augmented Reality', icon: FaVrCardboard, color: 'bg-purple-600 text-white' },
  vr: { name: 'Virtual Reality', icon: FaVrCardboard, color: 'bg-blue-600 text-white' }
};

// Helper function to convert complex technology objects to simple string arrays
const enrichTechnologiesToStrings = (techs: (string | { name: string } | Technology)[] | undefined): string[] => {
  if (!techs) return [];
  return techs.map(tech => {
    if (typeof tech === 'string') return tech;
    return tech.name;
  }).filter(Boolean); // Filter out any potential null/undefined names
};

// Ordenar proyectos: primero los que tienen video o imagen
const sortProjectsWithMediaFirst = <T extends { videoUrl?: string | null; imageUrl?: string | null }>(projects: T[]): T[] => {
  return [...projects].sort((a, b) => {
    const aHasMedia = !!a.videoUrl || !!a.imageUrl;
    const bHasMedia = !!b.videoUrl || !!b.imageUrl;
    if (aHasMedia === bHasMedia) return 0;
    return aHasMedia ? -1 : 1;
  });
};

// Company Projects
const companyProjects: CompanyProject[] = [
  {
    id: '1',
    title: 'TOKII Digital Twin Platform',
    description: 'Main product of company. Led product development of TOKII, the flagship digital twin platform for industrial equipment monitoring and predictive maintenance',
    longDescription: 'As Product Manager of TOKII (IMMERSIA&apos;s flagship product), led the complete product lifecycle from conception to deployment across Windows, AR, and VR platforms.',
    technologies: [
      { name: 'Python', icon: FaPython, color: 'bg-blue-600 text-white' },
      { name: 'Unity', icon: SiUnity, color: 'bg-black text-white' },
      { name: 'Docker', icon: FaDocker, color: 'bg-blue-500 text-white' },
      { name: 'PostgreSQL', icon: SiPostgresql, color: 'bg-blue-800 text-white' }
    ],
    imageUrl: 'https://immersia.eu/wp-content/uploads/vicinay.png.avif',
    role: 'Product Manager & Digital Twins Developer',
    achievements: ['Product Strategy & Roadmap', 'Cross-platform Development', 'Team Leadership', 'Agile Methodologies'],
    sector: 'Product Management',
    yearDeveloped: 2025
  },
  {    
    id: '2',
    title: 'NO-CODE ML Platform',
    description: 'AutoML platform for generating custom predictions and KPI dashboards',
    longDescription: 'No-code tool developed with scikit-learn and Flask to enable customers to generate custom predictions and KPI dashboards tailored to the information they seek, using their own business data.',
    technologies: [
      { name: 'Python', icon: FaPython, color: 'bg-blue-600 text-white' },
      { name: 'PyTorch', icon: SiPytorch, color: 'bg-yellow-600 text-white' },
      { name: 'Pandas', icon: SiPandas, color: 'bg-blue-800 text-white' },
      { name: 'Matplotlib', icon: FaChartLine, color: 'bg-blue-700 text-white' },
      { name: 'NumPy', icon: SiNumpy, color: 'bg-blue-600 text-white' },
      { name: 'Scikit-learn', icon: SiScikitlearn, color: 'bg-orange-500 text-white' },
      { name: 'Flask', icon: SiFlask, color: 'bg-gray-800 text-white' },
      { name: 'Scikit-learn', icon: SiScikitlearn, color: 'bg-orange-500 text-white' },
    ],
    imageUrl: 'https://immersia.eu/wp-content/uploads/primetals-1.png.avif',
    role: 'ML Engineer & Product Developer',
    achievements: ['Platform NO-CODE', 'Custom Predictions', 'Dashboards of KPIs', 'AutoML Enterprise'],
    sector: 'Machine Learning & Business Intelligence',
    yearDeveloped: 2025
  },
  {
    id: '3',
    title: 'TOKII AR - Augmented Reality Module',
    description: 'AR application for geopositioned data visualization with BIM information overlay and incident management',
    longDescription: 'Revolutionary AR application that connects industrial data and displays it geopositioned, with capabilities to show incidents and BIM information in real-world contexts.',
    technologies: [
      { name: 'Unity', icon: SiUnity, color: 'bg-black text-white' },
      { name: 'Augmented Reality', icon: FaVrCardboard, color: 'bg-purple-600 text-white' },
      { name: 'C#', icon: SiSharp, color: 'bg-purple-600 text-white' }
    ],
    imageUrl: 'https://immersia.eu/wp-content/uploads/acciona1.png.avif',
    role: 'AR Developer',
    achievements: ['Geopositioned Data Visualization', 'BIM Information Integration', 'Incident Management System', 'Real-world Data Overlay'],
    sector: 'Augmented Reality',
    yearDeveloped: 2024
  },
  {
    id: '4',
    title: 'TOKII VR - Industrial Training & Monitoring',
    description: 'Comprehensive VR solutions for industrial training, real-time monitoring, and digital twin visualization',
    longDescription: 'Multiple VR projects including immersive training environments, touchless monitoring systems, and SCADA-integrated digital twins for industrial automation.',
    technologies: [
      { name: 'Unity', icon: SiUnity, color: 'bg-black text-white' },
      { name: 'Virtual Reality', icon: FaVrCardboard, color: 'bg-blue-600 text-white' },
      { name: 'C#', icon: SiSharp, color: 'bg-purple-600 text-white' },
      { name: 'Kinect', icon: FaVrCardboard, color: 'bg-green-600 text-white' },
      { name: 'SCADA Integration', icon: FaServer, color: 'bg-orange-600 text-white' }
    ],
    imageUrl: 'https://immersia.eu/wp-content/uploads/acciona-1.png.avif',
    role: 'VR Developer & Digital Twin Specialist',
    achievements: [
      'Immersive Training Modules',
      'Touchless Monitoring Systems', 
      'Real-time Plant Monitoring',
      'SCADA Integration',
      'Digital Twin Visualization',
      'BMW Truck & Wheel Project',
      'ACCIONA Recycling Plant VR'
    ],
    sector: 'Virtual Reality & Industrial Automation',
    yearDeveloped: 2024
  },
];

// Static Academic Projects
const staticProjects: PortfolioProject[] = [
  {
    id: 'text-classification-transformers',
    title: 'Text Classification with Transformers',
    description: 'Advanced NLP project using BERT and transformer models for text classification tasks',
    longDescription: 'Implementation of state-of-the-art transformer models for multi-class text classification with fine-tuning capabilities.',
    category: 'ai-ml',
    technologies: [
      { name: 'Python', icon: FaPython, color: 'bg-blue-600 text-white' },
      { name: 'Transformers', icon: FaBrain, color: 'bg-purple-700 text-white' },
      { name: 'Hugging Face', icon: FaRobot, color: 'bg-yellow-600 text-white' },
      { name: 'PyTorch', icon: SiPytorch, color: 'bg-red-600 text-white' }
    ],
    featured: false,
    aiPowered: true,
    academicProject: true,
    complexity: 'advanced',
    achievements: ['BERT Implementation', 'Multi-class Classification', 'Model Fine-tuning'],
    yearDeveloped: 2024
  },
  {
    id: 'flower-classification-cv',
    title: 'Flower Classification Computer Vision',
    description: 'Deep learning model for flower species classification using convolutional neural networks',
    longDescription: 'Computer vision project implementing CNN architectures for accurate flower species identification and classification.',
    category: 'ai-ml',
    technologies: [
      { name: 'Python', icon: FaPython, color: 'bg-blue-600 text-white' },
      { name: 'TensorFlow', icon: SiTensorflow, color: 'bg-orange-600 text-white' },
      { name: 'OpenCV', icon: SiOpencv, color: 'bg-green-600 text-white' },
      { name: 'NumPy', icon: SiNumpy, color: 'bg-blue-600 text-white' }
    ],
    featured: false,
    aiPowered: true,
    academicProject: true,
    complexity: 'advanced',
    achievements: ['CNN Architecture', 'Image Preprocessing', 'High Accuracy Classification'],
    yearDeveloped: 2024
  },
  {
    id: 'bike-rental-prediction',
    title: 'Bike Rental Prediction',
    description: 'Machine learning model to predict bike rental demand using regression techniques',
    longDescription: 'Time series forecasting and regression analysis for predicting bike sharing demand patterns.',
    category: 'ai-ml',
    technologies: [
      { name: 'Python', icon: FaPython, color: 'bg-blue-600 text-white' },
      { name: 'Scikit-learn', icon: SiScikitlearn, color: 'bg-orange-500 text-white' },
      { name: 'Pandas', icon: SiPandas, color: 'bg-blue-800 text-white' },
      { name: 'Matplotlib', icon: FaChartLine, color: 'bg-blue-700 text-white' }
    ],
    aiPowered: true,
    academicProject: true,
    featured: false,
    complexity: 'intermediate',
    achievements: ['Regression Analysis', 'Feature Engineering', 'Time Series Forecasting'],
    yearDeveloped: 2024
  },
  {
    id: 'svm-random-forest',
    title: 'SVM & Random Forest Classification',
    description: 'Comparative study of SVM and Random Forest algorithms for classification tasks',
    longDescription: 'Comprehensive analysis and comparison of different machine learning algorithms for classification problems.',
    category: 'ai-ml',
    technologies: [
      { name: 'Python', icon: FaPython, color: 'bg-blue-600 text-white' },
      { name: 'Scikit-learn', icon: SiScikitlearn, color: 'bg-orange-500 text-white' },
      { name: 'NumPy', icon: SiNumpy, color: 'bg-blue-600 text-white' },
      { name: 'Seaborn', icon: FaChartLine, color: 'bg-teal-600 text-white' }
    ],
    aiPowered: true,
    academicProject: true,
    featured: false,
    complexity: 'intermediate',
    achievements: ['Algorithm Comparison', 'Performance Analysis', 'Feature Selection'],
    yearDeveloped: 2024
  },
  {
    id: 'clustering-anomaly-detection',
    title: 'Clustering & Anomaly Detection',
    description: 'Unsupervised learning techniques for data clustering and anomaly detection',
    longDescription: 'Implementation of K-Means clustering and various anomaly detection algorithms for pattern discovery.',
    category: 'ai-ml',
    technologies: [
      { name: 'Python', icon: FaPython, color: 'bg-blue-600 text-white' },
      { name: 'Scikit-learn', icon: SiScikitlearn, color: 'bg-orange-500 text-white' },
      { name: 'Matplotlib', icon: FaChartLine, color: 'bg-blue-700 text-white' },
      { name: 'NumPy', icon: SiNumpy, color: 'bg-blue-600 text-white' }
    ],
    aiPowered: true,
    academicProject: true,
    featured: false,
    complexity: 'intermediate',
    achievements: ['K-Means Clustering', 'Outlier Detection', 'Unsupervised Learning'],
    yearDeveloped: 2024
  },
  {
    id: 'air-quality-analysis',
    title: 'Air Quality Analysis',
    description: 'Data analysis and visualization of air quality patterns using statistical methods',
    longDescription: 'Comprehensive analysis of environmental data with statistical modeling and predictive analytics.',
    category: 'ai-ml',
    technologies: [
      { name: 'Python', icon: FaPython, color: 'bg-blue-600 text-white' },
      { name: 'Pandas', icon: SiPandas, color: 'bg-blue-800 text-white' },
      { name: 'Plotly', icon: FaChartLine, color: 'bg-purple-600 text-white' },
      { name: 'NumPy', icon: SiNumpy, color: 'bg-blue-600 text-white' }
    ],
    aiPowered: false,
    academicProject: true,
    featured: false,
    complexity: 'intermediate',
    achievements: ['Statistical Analysis', 'Data Visualization', 'Environmental Modeling'],
    yearDeveloped: 2024
  }
];

type ProjectSource = CompanyProject | PortfolioProject | DynamicProject;

// Function to automatically categorize projects based on their technologies
const categorizeProjectByTechnologies = (technologies: (string | { name: string })[] | undefined): ProjectCategory => {
  if (!technologies || technologies.length === 0) return 'all';
  
  // Convert all technologies to lowercase strings for easier matching
  const techNames = technologies.map(tech => 
    typeof tech === 'string' ? tech.toLowerCase() : tech.name.toLowerCase()
  );
  
  // AI/ML Technologies
  const aiMlTechs = [
    'python', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
    'machine learning', 'huggingface', 'transformers', 'opencv', 'jupyter',
    'gradio', 'langchain', 'gemini', 'chatgpt', 'ai', 'ml', 'nlp', 'faiss',
    'embeddings', 'neural networks', 'deep learning', 'computer vision'
  ];
  
  // Web Development Technologies  
  const webTechs = [
    'react', 'nextjs', 'next.js', 'javascript', 'typescript', 'nodejs', 'node.js',
    'fastapi', 'flask', 'django', 'html', 'css', 'tailwind', 'bootstrap',
    'mysql', 'postgresql', 'mongodb', 'express', 'vue', 'angular', 'docker',
    'ai-powered', 'gemini-api', 'mysql', 'sequelize', 'sqlite'
  ];
  
  // Game Development Technologies
  const gameTechs = [
    'unity', 'unreal', 'c#', 'csharp', 'blender', 'game', 'videogames',
    'shooter', 'tanks', 'turn-based', 'survival', 'covid-19', 'horror-game',
    'challenge', '3d', 'unity3d'
  ];
  
  // Health Tech Technologies
  const healthTechs = [
    'health', 'medical', 'healthcare', 'nutrition', 'calories', 'kcal',
    'stroke', 'predictor', 'android', 'opencv', 'tensorflow', 'ai-powered'
  ];
  
  // Enterprise/VR-AR Technologies
  const enterpriseTechs = [
    'vr', 'ar', 'virtual reality', 'augmented reality', 'enterprise',
    'industrial', 'scada', 'digital twin', 'immersive', 'hololens'
  ];
  
  // Count matches for each category
  const aiMlCount = techNames.filter(tech => aiMlTechs.some(aiTech => tech.includes(aiTech))).length;
  const webCount = techNames.filter(tech => webTechs.some(webTech => tech.includes(webTech))).length;
  const gameCount = techNames.filter(tech => gameTechs.some(gameTech => tech.includes(gameTech))).length;
  const healthCount = techNames.filter(tech => healthTechs.some(healthTech => tech.includes(healthTech))).length;
  const enterpriseCount = techNames.filter(tech => enterpriseTechs.some(entTech => tech.includes(entTech))).length;
  
  // Return the category with the highest match count
  const maxCount = Math.max(aiMlCount, webCount, gameCount, healthCount, enterpriseCount);
  
  if (maxCount === 0) return 'all';
  
  if (aiMlCount === maxCount) return 'ai-ml';
  if (webCount === maxCount) return 'full-stack';
  if (gameCount === maxCount) return 'game-dev';
  if (healthCount === maxCount) return 'health-tech';
  if (enterpriseCount === maxCount) return 'enterprise';
  
  return 'all';
};

// The single, definitive normalization function, now fully type-safe
const normalizeProject = (project: ProjectSource): Project => {
  const now = new Date().toISOString();
  
  // The `technologies` property in ProjectCard expects a string array.
  const technologyNames = enrichTechnologiesToStrings(project.technologies);
  
  // Auto-categorize dynamic projects based on their technologies
  let projectCategory: ProjectCategory = 'all';
  if ('category' in project && project.category) {
    projectCategory = project.category;
    } else {
    // For dynamic projects without explicit category, categorize by technologies
    projectCategory = categorizeProjectByTechnologies(project.technologies);
    }

  return {
    id: String(project.id),
    title: project.title || '',
    description: project.description || '',
    imageUrl: 'imageUrl' in project ? project.imageUrl || null : null,
    videoUrl: 'videoUrl' in project ? project.videoUrl || null : null,
    githubUrl: 'githubUrl' in project ? project.githubUrl || null : ('github_url' in project ? project.github_url || null : null),
    liveUrl: 'liveUrl' in project ? project.liveUrl || null : ('live_url' in project ? project.live_url || null : null),
    technologies: technologyNames,
    is_featured: 'is_featured' in project ? project.is_featured === true : ('featured' in project ? project.featured === true : false),
    category: projectCategory,
    created_at: ('created_at' in project && typeof project.created_at === 'string') ? project.created_at : now,
    updated_at: ('updated_at' in project && typeof project.updated_at === 'string') ? project.updated_at : now,
  };
};

// Main API call function
const fetchDynamicProjects = async (): Promise<DynamicProject[]> => {
  try {
    const response = await apiClient<PaginatedProjectsResponse>('/projects/');
    if (response && Array.isArray(response.items)) {
      return response.items;
    }
    console.warn('Fetched projects data is not in the expected format:', response);
    return [];
  } catch (error) {
    console.error('Error fetching projects:', error);
    return [];
  }
};

function PortfolioGrid() {
  const { user, token } = useAuth();
  const [showModal, setShowModal] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);

  const [dynamicProjects, setDynamicProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState<ProjectCategory>('all');
  const [showAllOtherProjects, setShowAllOtherProjects] = useState(false);

  // Normalize static projects only once, as they don't change.
  const normalizedStaticProjects = useMemo(() => staticProjects.map(normalizeProject), []);
  
  const fetchProjectsCallback = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const dynamicData = await fetchDynamicProjects();
      const normalized = dynamicData.map(normalizeProject);
      setDynamicProjects(normalized);
    } catch (err) {
      console.error("Failed to load dynamic projects from API:", err);
      setError(err instanceof Error ? err.message : 'Failed to load projects');
      // If API fails, we still have the static projects.
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProjectsCallback();
  }, [fetchProjectsCallback]);

  // Featured projects son SOLO de la base de datos (dynamicProjects)
  const featuredProjects = useMemo(() => {
    const staticFeatured = normalizedStaticProjects.filter(p => p.is_featured);
    const dynamicFeatured = dynamicProjects.filter(p => p.is_featured);
    const allFeatured = [...staticFeatured, ...dynamicFeatured];
    // Aplicar filtro de categoría y ordenar con media primero
    const filtered = activeCategory === 'all' 
      ? allFeatured 
      : allFeatured.filter(p => p.category === activeCategory);
    return sortProjectsWithMediaFirst(filtered);
  }, [normalizedStaticProjects, dynamicProjects, activeCategory]);
  
  // Otros proyectos: todos los estáticos/company + los dinámicos no destacados
  const otherProjects = useMemo(() => {
    const staticNonFeatured = normalizedStaticProjects.filter(p => !p.is_featured);
    const dynamicNonFeatured = dynamicProjects.filter(p => !p.is_featured);
    const allOther = [...staticNonFeatured, ...dynamicNonFeatured];
    // Aplicar filtro de categoría y ordenar con media primero
    const filtered = activeCategory === 'all' 
      ? allOther 
      : allOther.filter(p => p.category === activeCategory);
    return sortProjectsWithMediaFirst(filtered);
  }, [normalizedStaticProjects, dynamicProjects, activeCategory]);

  // Displayed other projects with pagination
  const displayedOtherProjects = useMemo(() => {
    const maxInitialProjects = 6;
    if (showAllOtherProjects || otherProjects.length <= maxInitialProjects) {
      return otherProjects;
    }
    return otherProjects.slice(0, maxInitialProjects);
  }, [otherProjects, showAllOtherProjects]);

  // Enterprise projects con filtro de categoría aplicado y ordenados con media primero
  const filteredEnterpriseProjects = useMemo(() => {
    // Mantenerlos como CompanyProject, pero ordenados
    const filtered = activeCategory === 'all' 
      ? companyProjects 
      : companyProjects.filter(p => {
          // Mapear sector a categoría
          const categoryMapping: Record<string, ProjectCategory> = {
            'Product Management': 'enterprise',
            'Machine Learning & Business Intelligence': 'ai-ml',
            'Augmented Reality': 'enterprise',
            'Virtual Reality & Industrial Automation': 'enterprise'
          };
          return categoryMapping[p.sector] === activeCategory;
        });
    return sortProjectsWithMediaFirst(filtered);
  }, [activeCategory]);

  const handleCreateProject = () => {
    setEditingProject(null);
    setShowModal(true);
  };

  const handleEditProject = (project: Project) => {
    setEditingProject(project);
    setShowModal(true);
  };

  const handleDeleteProject = async (projectId: string) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      try {
        if (!token) {
          alert("You must be logged in to delete projects.");
      return;
    }
        await apiClient(`/projects/${projectId}`, { method: 'DELETE', token });
        fetchProjectsCallback();
      } catch (err) {
        console.error("Failed to delete project:", err);
        alert("Error deleting project.");
      }
    }
  };

  const handleModalSave = () => {
    fetchProjectsCallback();
  };

  // Remove the old filteredProjects logic since we now filter in each section
  const categoryCounts = useMemo(() => {
    // Count all projects from all sections
    const allProjects = [
      ...normalizedStaticProjects,
      ...dynamicProjects,
      // Count company projects with proper category mapping
      ...companyProjects.map(p => {
        const categoryMapping: Record<string, ProjectCategory> = {
          'Product Management': 'enterprise',
          'Machine Learning & Business Intelligence': 'ai-ml',
          'Augmented Reality': 'enterprise',
          'Virtual Reality & Industrial Automation': 'enterprise'
        };
        return { ...normalizeProject(p), category: categoryMapping[p.sector] || 'enterprise' };
      })
    ];
    
    const counts: Record<ProjectCategory, number> = {
      'all': allProjects.length,
      'ai-ml': 0,
      'full-stack': 0,
      'game-dev': 0,
      'health-tech': 0,
      'enterprise': 0
    };
    
    allProjects.forEach(p => {
      if (p.category && counts[p.category] !== undefined) {
        counts[p.category]++;
      }
    });
    
    return counts;
  }, [normalizedStaticProjects, dynamicProjects]);

  // Category filter change should reset the "show all" state
  const handleCategoryChange = (category: ProjectCategory) => {
    setActiveCategory(category);
    setShowAllOtherProjects(false);
  };

  const handleShowMoreProjects = () => {
    setShowAllOtherProjects(true);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-20">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="bg-card h-48 rounded-t-lg mb-4"></div>
                <div className="space-y-2">
                  <div className="h-4 bg-card rounded w-3/4"></div>
                  <div className="h-4 bg-card rounded w-1/2"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    console.error('Portfolio error:', error);
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <AnimatedSection className="pt-20 pb-16">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
              Portfolio
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground mb-8">
              Specialized in <span className="text-primary font-semibold">Machine Learning and Generative AI solutions</span>
            </p>
            <div className="flex flex-wrap justify-center gap-4 mb-8">
              <Badge variant="outline" className="px-4 py-2">
                <FaBrain className="mr-2 h-4 w-4" />
                Official Master in AI
              </Badge>
              <Badge variant="outline" className="px-4 py-2">
                <FaBuilding className="mr-2 h-4 w-4" />
                IMMERSIA Product Manager
              </Badge>
              <Badge variant="outline" className="px-4 py-2">
                <FaRobot className="mr-2 h-4 w-4" />
                AI-Powered Solutions
              </Badge>
            </div>
          </div>
        </div>
      </AnimatedSection>

      {/* Technology Skills Carousel */}
      <AnimatedSection className="py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-3 mb-6">
              <FaCode className="h-8 w-8 text-primary" />
              <h2 className="text-3xl font-bold">Technologies & Skills</h2>
            </div>
            <p className="text-xl text-muted-foreground">
              Complete tech stack for AI development and powered AI applications
            </p>
          </div>
          {/* Carousel wrapper con overflow-x-hidden para scroll infinito perfecto */}
          <div className="w-full overflow-x-hidden">
            <div
              className="flex flex-nowrap gap-8 py-8 hide-scrollbar animate-scroll md:animate-scroll"
              style={{ WebkitOverflowScrolling: 'touch', scrollSnapType: 'x mandatory' }}
            >
              {/* Primer pase */}
              {Object.values(technologies).map((tech, techIndex) => (
                <div
                  key={`a-${tech.name}-${techIndex}`}
                  className="flex-shrink-0 group tech-card snap-center min-w-[180px]"
                >
                  <div className="bg-card border rounded-xl p-6 text-center hover:shadow-2xl transition-all duration-500 hover:scale-110 hover:-translate-y-3 bg-gradient-to-br from-background to-muted/30">
                    <div className="flex items-center justify-center mb-4">
                      <div className={`p-3 rounded-full group-hover:scale-110 animate-float transition-all duration-300 ${tech.color}`}>
                        <tech.icon className="h-7 w-7" />
                      </div>
                    </div>
                    <h3 className="font-semibold text-sm text-center leading-tight group-hover:text-primary transition-colors duration-300">
                      {tech.name}
                    </h3>
                  </div>
                </div>
              ))}
              {/* Segundo pase (duplicado) */}
              {Object.values(technologies).map((tech, techIndex) => (
                <div
                  key={`b-${tech.name}-${techIndex}`}
                  className="flex-shrink-0 group tech-card snap-center min-w-[180px]"
                >
                  <div className="bg-card border rounded-xl p-6 text-center hover:shadow-2xl transition-all duration-500 hover:scale-110 hover:-translate-y-3 bg-gradient-to-br from-background to-muted/30">
                    <div className="flex items-center justify-center mb-4">
                      <div className={`p-3 rounded-full group-hover:scale-110 animate-float transition-all duration-300 ${tech.color}`}>
                        <tech.icon className="h-7 w-7" />
                      </div>
                    </div>
                    <h3 className="font-semibold text-sm text-center leading-tight group-hover:text-primary transition-colors duration-300">
                      {tech.name}
                    </h3>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-16">
            {[
              {
                title: 'AI & Machine Learning',
                icon: FaBrain,
                skills: ['TensorFlow', 'PyTorch', 'Scikit-learn', 'Hugging Face', 'Transformers', 'LangChain', 'AutoML', 'MLOps'],
                color: 'text-purple-600',
                bgColor: 'bg-gradient-to-br from-purple-50 to-purple-100'
              },
              {
                title: 'Generative AI & LLMs',
                icon: FaRobot,
                skills: ['Gemini AI', 'ChatGPT', 'Large Language Models', 'Ollama', 'Gradio', 'FAISS', 'Vector Databases'],
                color: 'text-pink-600',
                bgColor: 'bg-gradient-to-br from-pink-50 to-pink-100'
              },
              {
                title: 'Computer Vision & NLP',
                icon: FaEye,
                skills: ['OpenCV', 'YOLO', 'PIL/Pillow', 'BERT', 'Word Embeddings', 'Sentiment Analysis'],
                color: 'text-green-600',
                bgColor: 'bg-gradient-to-br from-green-50 to-green-100'
              },
              {
                title: 'Planning & Reasoning',
                icon: FaBrain,
                skills: ['PDDL', 'Prolog', 'Answer Set Programming', 'Search Algorithms', 'Cognitive Systems'],
                color: 'text-indigo-600',
                bgColor: 'bg-gradient-to-br from-indigo-50 to-indigo-100'
              },
              {
                title: 'Data Science',
                icon: FaChartLine,
                skills: ['Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Plotly', 'Jupyter', 'Google Colab'],
                color: 'text-blue-600',
                bgColor: 'bg-gradient-to-br from-blue-50 to-blue-100'
              },
              {
                title: 'Web Development',
                icon: FaCode,
                skills: ['Next.js', 'React', 'TypeScript', 'FastAPI', 'PostgreSQL', 'Docker'],
                color: 'text-cyan-600',
                bgColor: 'bg-gradient-to-br from-cyan-50 to-cyan-100'
              },
              {
                title: 'Game Development',
                icon: FaDesktop,
                skills: ['Unity', 'C#', 'Blender', 'VR/AR', 'Game Design', '3D Modeling'],
                color: 'text-orange-600',
                bgColor: 'bg-gradient-to-br from-orange-50 to-orange-100'
              },
              {
                title: 'DevOps & Agile',
                icon: FaServer,
                skills: ['Google Cloud', 'Docker', 'MLflow', 'Streamlit', 'Jira', 'Agile', 'Scrum', 'Team Leadership'],
                color: 'text-gray-600',
                bgColor: 'bg-gradient-to-br from-gray-50 to-gray-100'
              }
            ].map((category, index) => (
              <Card key={index} className="group hover:shadow-2xl transition-all duration-500 hover:scale-105 hover:-translate-y-2 border-0">
                <div className={`${category.bgColor} rounded-t-lg p-4`}>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-white/80 rounded-lg shadow-sm">
                      <category.icon className={`h-6 w-6 ${category.color}`} />
                    </div>
                    <CardTitle className="text-sm font-bold text-gray-800">{category.title}</CardTitle>
                  </div>
                </div>
                <CardContent className="pt-4">
                  <div className="flex flex-wrap gap-2">
                    {category.skills.map((skill, idx) => (
                      <Badge key={idx} variant="outline" className="text-xs px-3 py-1 hover:bg-primary/10 transition-colors">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </AnimatedSection>

        {/* Academic Formation Section */}
        <AnimatedSection className="py-16">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <div className="flex items-center justify-center gap-3 mb-6">
                <FaGraduationCap className="h-8 w-8 text-primary" />
                <h2 className="text-3xl font-bold">Academic Formation</h2>
              </div>
              <p className="text-xl text-muted-foreground">
                <strong>Master in Artificial Intelligence</strong> at <a href="https://www.unir.net/" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">UNIR</a> • <strong>6 specialized areas</strong>
              </p>
              <p className="text-lg text-muted-foreground">
                <strong>Computer Engineering</strong> at <a href="https://www.unileon.es/" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">Universidad de León</a>
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                title: 'Machine Learning',
                description: 'Linear regression, SVM, Random Forest, K-Means, anomaly detection, supervised & unsupervised learning',
                icon: FaRobot,
                projects: ['Bike Rental Prediction', 'SVM & Random Forest', 'Clustering & Anomaly Detection'],
                borderColor: 'border-blue-200'
              },
              {
                title: 'Natural Language Processing',
                description: 'Word Embeddings, Transformers, BERT, text classification, sentiment analysis, language models',
                icon: FaCode,
                projects: ['Text Classification with Transformers', 'Semantic Book Recommender'],
                borderColor: 'border-green-200'
              },
              {
                title: 'Computer Vision',
                description: 'Image processing, CNN, classification, contrast adjustment, OpenCV, deep learning for vision',
                icon: FaEye,
                projects: ['Flower Classification Computer Vision', 'My Kcal App'],
                borderColor: 'border-purple-200'
              },
              {
                title: 'Reasoning & Automated Planning',
                description: 'PDDL, search algorithms, automated planning, knowledge representation, logic programming',
                icon: FaBrain,
                projects: ['PDDL Planning Projects', 'Search Algorithm Implementations'],
                borderColor: 'border-orange-200'
              },
              {
                title: 'Artificial Cognitive Systems',
                description: 'Cognitive architectures, mind models, behavioral AI, cognitive computing, neurosymbolic systems',
                icon: FaBrain,
                projects: ['Cognitive System Modeling', 'Behavioral AI Experiments'],
                borderColor: 'border-pink-200'
              }
            ].map((area, index) => (
              <Card key={index} className={`group hover:shadow-lg transition-all duration-300 hover:scale-105 border-2 ${area.borderColor}`}>
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      <area.icon className="h-5 w-5 text-primary" />
                    </div>
                    <CardTitle className="text-lg">{area.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <CardDescription className="text-sm mb-3 leading-relaxed">
                    {area.description}
                  </CardDescription>
                  <div className="space-y-2">
                    <p className="text-xs font-medium text-muted-foreground">Related projects:</p>
                    <div className="flex flex-wrap gap-1">
                      {area.projects.map((project, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs px-2 py-1">
                          {project}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            </div>
          </div>
        </AnimatedSection>

        
        <div className="container mx-auto px-4 space-y-16">
        
        {/* Global Category Filters - Applied to all sections */}
        <AnimatedSection>
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-3 mb-6">
              <FaCode className="h-8 w-8 text-primary" />
              <h2 className="text-3xl font-bold">Project Categories</h2>
            </div>
            <p className="text-xl text-muted-foreground mb-8">
              Filter projects across all sections by technology and domain
            </p>
            
            {/* Category Filters */}
            <div className="flex flex-wrap justify-center gap-2 md:gap-4">
              {[
                { key: 'all', label: 'All Projects' },
                { key: 'ai-ml', label: 'AI & Machine Learning' },
                { key: 'full-stack', label: 'AI & Web Development' },
                { key: 'game-dev', label: 'Game Development' },
                { key: 'health-tech', label: 'Health Tech' },
                { key: 'enterprise', label: 'Enterprise & VR/AR' },
              ].map((category) => (
                <Button
                  key={category.key}
                  variant={activeCategory === category.key ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => handleCategoryChange(category.key as ProjectCategory)}
                  className="transition-all duration-300 hover:scale-105"
                >
                  {category.label}
                  <Badge variant="secondary" className="ml-2 text-xs px-1.5">
                    {categoryCounts[category.key as ProjectCategory]}
                  </Badge>
                </Button>
              ))}
            </div>
          </div>
        </AnimatedSection>

        {/* Featured Projects with Images/GIFs */}
        <AnimatedSection>
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-3 mb-6">
              <FaStar className="h-8 w-8 text-yellow-500" />
              <h2 className="text-3xl font-bold">Featured Projects</h2>
              {user?.is_superuser && (
                <Button
                  onClick={handleCreateProject}
                  className="ml-4"
                  size="sm"
                >
                  <FaPlus className="h-4 w-4 mr-2" />
                  Nuevo Proyecto
                </Button>
              )}
            </div>
            <p className="text-xl text-muted-foreground">
              Highlighted projects with visual demonstrations
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 auto-rows-max">
            {featuredProjects.map((project) => (
              <div key={project.id} className="relative group">
              <ProjectCard 
                  project={project} 
                  isSuperuser={user?.is_superuser}
                  onToggleFeatured={() => { /* Implement if needed */ }}
                />
                {user?.is_superuser && 'id' in project && (
                  <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleEditProject(project)}
                      className="bg-white/90 backdrop-blur-sm h-8 w-8"
                    >
                      <FaEdit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleDeleteProject(project.id)}
                      className="text-red-600 hover:text-red-700 bg-white/90 backdrop-blur-sm h-8 w-8"
                    >
                      <FaTrash className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </AnimatedSection>

        {/* Other Projects Section */}
        <AnimatedSection className="py-16">
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-3 mb-6">
              <FaCode className="h-8 w-8 text-primary" />
              <h2 className="text-3xl font-bold">Other Projects</h2>
            </div>
            <p className="text-xl text-muted-foreground">
              Complete collection of academic and personal projects
            </p>
          </div>

          {/* Projects Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 auto-rows-max">
            {displayedOtherProjects.map((project) => (
              <div key={project.id} className="relative group">
              <ProjectCard 
                key={project.id} 
                  project={project} 
                isSuperuser={user?.is_superuser}
                  onToggleFeatured={() => { /* Implement if needed */ }}
                />
                {user?.is_superuser && 'id' in project && (
                  <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleEditProject(project)}
                      className="bg-white/90 backdrop-blur-sm h-8 w-8"
                    >
                      <FaEdit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleDeleteProject(project.id)}
                      className="text-red-600 hover:text-red-700 bg-white/90 backdrop-blur-sm h-8 w-8"
                    >
                      <FaTrash className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Show More Button */}
          {!showAllOtherProjects && otherProjects.length > 6 && (
            <div className="text-center mt-8">
              <Button
                onClick={handleShowMoreProjects}
                variant="outline"
                size="lg"
                className="group hover:scale-105 transition-all duration-300"
              >
                Ver más proyectos ({otherProjects.length - 6} restantes)
                <FaPlus className="ml-2 h-4 w-4 transition-transform group-hover:rotate-90" />
              </Button>
            </div>
          )}
        </AnimatedSection>

        {/* Enterprise Projects Section */}
        <AnimatedSection className="py-16">
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-3 mb-6">
              <FaBuilding className="h-8 w-8 text-primary" />
              <h2 className="text-3xl font-bold">Enterprise Projects</h2>
          </div>
            <p className="text-xl text-muted-foreground mb-4">
              Product Manager & Digital Twins Developer at <strong><a href="https://immersia.eu/" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">IMMERSIA</a></strong>
            </p>
            <div className="max-w-4xl mx-auto text-center">
              <p className="text-sm text-muted-foreground mb-6">
                Leading TOKII product development with expertise in <span className="font-semibold text-primary">team collaboration</span>, 
                <span className="font-semibold text-primary"> Jira task management</span>, <span className="font-semibold text-primary">agile methodologies</span>, 
                and <span className="font-semibold text-primary">complete product lifecycle management</span>. 
                Developed solutions for diferent sectors (industry, manufacturing, education, smart cities, etc.) and cross-platform (Windows, AR, and VR) with advanced geopositioned data visualization and BIM integration.
              </p>
        </div>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredEnterpriseProjects.map((project) => (
              <Card key={project.id} className="group relative overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-2 bg-gradient-to-br from-background to-muted/30">
                {project.imageUrl && (
                  <div className="relative h-48 overflow-hidden">
                    <img
                      src={project.imageUrl}
                      alt={project.title}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      loading="eager"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  </div>
                )}
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Badge variant="outline" className="text-xs bg-primary/10">
                      {project.sector}
                    </Badge>
                    <Badge variant="secondary" className="text-xs">
                      {project.yearDeveloped}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      <FaBuilding className="mr-1 h-3 w-3" />
                      IMMERSIA
                    </Badge>
                  </div>
                  <h3 className="text-lg font-bold mb-2 group-hover:text-primary transition-colors">{project.title}</h3>
                  <p className="text-sm text-muted-foreground mb-4">{project.description}</p>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {project.technologies.slice(0, 3).map((tech) => (
                      <Badge key={tech.name} variant="secondary" className="text-xs">
                        <tech.icon className="mr-1 h-3 w-3" />
                        {tech.name}
                      </Badge>
                    ))}
                  </div>
                  <div className="space-y-2 mb-4">
                    {project.achievements.slice(0, 3).map((achievement, idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 bg-primary rounded-full"></div>
                        <span className="text-xs text-muted-foreground">{achievement}</span>
                      </div>
                    ))}
                  </div>
                  <div className="text-xs text-primary font-medium">
                    Role: {project.role}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </AnimatedSection>


      </div>

      {/* CTA Section */}
      <AnimatedSection className="py-16">
        <div className="container mx-auto px-4 text-center">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Interested in collaborating?
            </h2>
            <p className="text-lg text-muted-foreground mb-8">
              I&apos;m always open to new challenging projects in AI, digital twins development, and AutoML.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/contact">
                <Button size="lg" className="group">
                  Contact Me
                  <FaExternalLinkAlt className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Button>
              </Link>
              <a href="https://github.com/ivanintech" target="_blank" rel="noopener noreferrer">
                <Button variant="outline" size="lg" className="group">
                  <FaGithub className="mr-2 h-4 w-4" />
                  View GitHub
                  <FaExternalLinkAlt className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Button>
              </a>
            </div>
          </div>
        </div>
      </AnimatedSection>

      {/* Modal de administración de proyectos */}
      <ProjectModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onSave={handleModalSave}
        project={editingProject || undefined}
      />
    </div>
  );
}

export default function PortfolioPage() {
  return <PortfolioGrid />;
} 