import React, { useState, useRef, useEffect } from 'react';
import '../styles/SearchForm.css';

// Common cities and locations for autocomplete
const LOCATION_SUGGESTIONS = [
  // Major Indian Cities
  'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune', 'Ahmedabad',
  'Jaipur', 'Surat', 'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Thane', 'Bhopal',
  'Visakhapatnam', 'Patna', 'Vadodara', 'Ghaziabad', 'Ludhiana', 'Agra', 'Nashik',
  'Faridabad', 'Meerut', 'Rajkot', 'Varanasi', 'Srinagar', 'Amritsar', 'Allahabad',
  'Ranchi', 'Howrah', 'Jabalpur', 'Gwalior', 'Vijayawada', 'Jodhpur', 'Raipur',
  'Kota', 'Guwahati', 'Chandigarh', 'Thiruvananthapuram', 'Solapur', 'Hubli',
  'Tiruchirappalli', 'Tiruppur', 'Moradabad', 'Mysore', 'Bareilly', 'Gurgaon',
  'Aligarh', 'Jalandhar', 'Bhubaneswar', 'Salem', 'Warangal', 'Guntur', 'Bhiwandi',
  'Saharanpur', 'Gorakhpur', 'Bikaner', 'Amravati', 'Noida', 'Jamshedpur', 'Bhilai',
  'Cuttack', 'Firozabad', 'Kochi', 'Nellore', 'Bhavnagar', 'Dehradun', 'Durgapur',
  'Asansol', 'Rourkela', 'Nanded', 'Kolhapur', 'Ajmer', 'Akola', 'Gulbarga',
  'Jamnagar', 'Ujjain', 'Loni', 'Siliguri', 'Jhansi', 'Ulhasnagar', 'Jammu',
  'Sangli-Miraj', 'Mangalore', 'Erode', 'Belgaum', 'Ambattur', 'Tirunelveli',
  'Malegaon', 'Gaya', 'Jalgaon', 'Udaipur', 'Maheshtala', 'Tirupati', 'Karnal',
  'Sangareddy', 'Nadiad', 'Bokaro Steel City', 'Parbhani', 'Satara', 'Bijapur',
  'Kurnool', 'Rajahmundry', 'Raichur', 'Bardhaman', 'Kulti', 'Nizamabad',
  'Parbhani', 'Tumkur', 'Khammam', 'Ozhukarai', 'Bihar Sharif', 'Panipat',
  'Darbhanga', 'Bally', 'Aizawl', 'Dewas', 'Ichalkaranji', 'Tinsukia', 'Ratlam',
  'Hapur', 'Arrah', 'Anantapur', 'Karimnagar', 'Etawah', 'Bharatpur', 'Begusarai',
  'New Delhi', 'Gandhinagar', 'Baranagar', 'Tiruvottiyur', 'Puducherry', 'Sikar',
  'Thoothukudi', 'Rewa', 'Mirzapur', 'Raigarh', 'Pali', 'Ramagundam', 'Haridwar',
  'Vijayanagaram', 'Katihar', 'Nagercoil', 'Sri Ganganagar', 'Karawal Nagar',
  'Mango', 'Thanjavur', 'Bulandshahr', 'Uluberia', 'Murwara', 'Sambhal',
  'Singrauli', 'Nadiad', 'Naihati', 'Yamunanagar', 'Bidhannagar', 'Pallavaram',
  'Bidar', 'Munger', 'Panchkula', 'Burhanpur', 'Raurkela Industrial Township',
  'Kharagpur', 'Dindigul', 'Gandhinagar', 'Hospet', 'Nangloi Jat', 'Malda',
  'Ongole', 'Deoghar', 'Chapra', 'Puri', 'Haldia', 'Khandwa', 'Nandyal',
  'Morena', 'Amroha', 'Anand', 'Bhind', 'Bhalswa Jahangir Pur', 'Madhyamgram',
  'Bhiwani', 'Berhampore', 'Ambala', 'Morbi', 'Fatehpur', 'Raebareli', 'Khora',
  'Chittoor', 'Bhusawal', 'Orai', 'Bahraich', 'Phusro', 'Vellore', 'Mehsana',
  'Rewa', 'Uran Islampur', 'Rae Bareli', 'Jhunjhunu', 'Sikar', 'Sitapur',
  'Shahjahanpur', 'Lakhimpur', 'Hardoi', 'Basti', 'Azamgarh', 'Rampur',
  'Shamli', 'Aligarh', 'Kasganj', 'Etah', 'Firozabad', 'Mainpuri', 'Budaun',
  'Bareilly', 'Pilibhit', 'Shahjahanpur', 'Lakhimpur Kheri', 'Sitapur',
  'Hardoi', 'Unnao', 'Lucknow', 'Rae Bareli', 'Amethi', 'Sultanpur', 'Pratapgarh',
  'Kaushambi', 'Allahabad', 'Fatehpur', 'Banda', 'Chitrakoot', 'Hamirpur',
  'Mahoba', 'Lalitpur', 'Jhansi', 'Jalaun', 'Orai', 'Etawah', 'Auraiya',
  'Kannauj', 'Farrukhabad', 'Mainpuri', 'Etah', 'Kasganj', 'Aligarh',
  'Hathras', 'Mathura', 'Agra', 'Firozabad', 'Etah', 'Mainpuri', 'Budaun',
  'Bareilly', 'Pilibhit', 'Shahjahanpur', 'Lakhimpur Kheri', 'Sitapur',
  // States
  'Maharashtra', 'Karnataka', 'Tamil Nadu', 'Gujarat', 'Rajasthan', 'Uttar Pradesh',
  'West Bengal', 'Madhya Pradesh', 'Bihar', 'Andhra Pradesh', 'Telangana', 'Kerala',
  'Odisha', 'Punjab', 'Haryana', 'Jharkhand', 'Assam', 'Chhattisgarh', 'Himachal Pradesh',
  'Uttarakhand', 'Tripura', 'Meghalaya', 'Manipur', 'Nagaland', 'Goa', 'Arunachal Pradesh',
  'Mizoram', 'Sikkim', 'Delhi', 'Puducherry', 'Chandigarh', 'Dadra and Nagar Haveli',
  'Daman and Diu', 'Lakshadweep', 'Andaman and Nicobar Islands',
  // Countries
  'India', 'United States', 'United Kingdom', 'Canada', 'Australia', 'Singapore',
  'United Arab Emirates', 'Germany', 'France', 'Japan', 'China',
  // Remote / generic
  'Remote', 'Work From Home'
];

// Common skills, roles and designations for autocomplete
const KEYWORD_SUGGESTIONS = [
  // Roles
  'Software Engineer', 'Frontend Developer', 'Backend Developer', 'Full Stack Developer',
  'React Developer', 'Node.js Developer', 'Python Developer', 'Java Developer',
  'Data Scientist', 'Data Analyst', 'Machine Learning Engineer', 'DevOps Engineer',
  'Site Reliability Engineer', 'Cloud Engineer', 'Product Manager', 'Project Manager',
  'Business Analyst', 'QA Engineer', 'Automation Tester', 'UI/UX Designer',
  'Graphic Designer', 'Web Designer', 'Mobile App Developer', 'Android Developer',
  'iOS Developer', 'Flutter Developer', 'React Native Developer',
  // Skills / stacks
  'React', 'React.js', 'Next.js', 'Angular', 'Vue.js', 'JavaScript', 'TypeScript',
  'HTML', 'CSS', 'Tailwind CSS', 'Bootstrap', 'SASS', 'Redux',
  'Node.js', 'Express.js', 'Django', 'Flask', 'FastAPI', 'Spring Boot',
  'Python', 'Java', 'C++', 'C#', '.NET', 'Go', 'Rust', 'PHP', 'Laravel',
  'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
  'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'CI/CD',
  'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision',
  'Pandas', 'NumPy', 'TensorFlow', 'PyTorch', 'Scikit-learn',
  // Domains
  'Web Development', 'Backend Development', 'Frontend Development',
  'Full Stack Development', 'Data Engineering', 'Cyber Security',
  'Digital Marketing', 'SEO Specialist', 'Content Writer'
];

const SearchForm = ({ onSearch, loading }) => {
  const [formData, setFormData] = useState({
    job_type: 'internship',
    keyword: '',
    location: '',
    experience: '',
  });

  const [errors, setErrors] = useState({});

  // Location autocomplete state
  const [locationSuggestions, setLocationSuggestions] = useState([]);
  const [showLocationSuggestions, setShowLocationSuggestions] = useState(false);
  const [activeLocationSuggestionIndex, setActiveLocationSuggestionIndex] = useState(-1);
  const locationInputRef = useRef(null);
  const locationSuggestionsRef = useRef(null);

  // Keyword autocomplete state
  const [keywordSuggestions, setKeywordSuggestions] = useState([]);
  const [showKeywordSuggestions, setShowKeywordSuggestions] = useState(false);
  const [activeKeywordSuggestionIndex, setActiveKeywordSuggestionIndex] = useState(-1);
  const keywordInputRef = useRef(null);
  const keywordSuggestionsRef = useRef(null);

  // Filter location suggestions based on input
  useEffect(() => {
    if (formData.location.trim().length > 0) {
      const filtered = LOCATION_SUGGESTIONS.filter(location =>
        location.toLowerCase().includes(formData.location.toLowerCase())
      ).slice(0, 8); // Show max 8 suggestions
      setLocationSuggestions(filtered);
      // Only show suggestions if the value doesn't exactly match a suggestion (i.e., user is still typing)
      const exactMatch = LOCATION_SUGGESTIONS.some(
        loc => loc.toLowerCase() === formData.location.toLowerCase()
      );
      setShowLocationSuggestions(filtered.length > 0 && !exactMatch);
    } else {
      setLocationSuggestions([]);
      setShowLocationSuggestions(false);
    }
    setActiveLocationSuggestionIndex(-1);
  }, [formData.location]);

  // Filter keyword suggestions based on input
  useEffect(() => {
    if (formData.keyword.trim().length > 0) {
      const query = formData.keyword.toLowerCase();
      const filtered = KEYWORD_SUGGESTIONS.filter(item =>
        item.toLowerCase().includes(query)
      ).slice(0, 8); // Show max 8 suggestions
      setKeywordSuggestions(filtered);
      // Only show suggestions if the value doesn't exactly match a suggestion (i.e., user is still typing)
      const exactMatch = KEYWORD_SUGGESTIONS.some(
        item => item.toLowerCase() === query
      );
      setShowKeywordSuggestions(filtered.length > 0 && !exactMatch);
    } else {
      setKeywordSuggestions([]);
      setShowKeywordSuggestions(false);
    }
    setActiveKeywordSuggestionIndex(-1);
  }, [formData.keyword]);

  // Close suggestions when clicking outside either input / list
  useEffect(() => {
    const handleClickOutside = (event) => {
      const clickedInLocationInput =
        locationInputRef.current &&
        locationInputRef.current.contains(event.target);
      const clickedInLocationList =
        locationSuggestionsRef.current &&
        locationSuggestionsRef.current.contains(event.target);

      const clickedInKeywordInput =
        keywordInputRef.current &&
        keywordInputRef.current.contains(event.target);
      const clickedInKeywordList =
        keywordSuggestionsRef.current &&
        keywordSuggestionsRef.current.contains(event.target);

      const clickedInsideAny =
        clickedInLocationInput ||
        clickedInLocationList ||
        clickedInKeywordInput ||
        clickedInKeywordList;

      if (!clickedInsideAny) {
        setShowLocationSuggestions(false);
        setShowKeywordSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const handleKeywordSelect = (keyword) => {
    setFormData((prev) => ({
      ...prev,
      keyword,
    }));
    setShowKeywordSuggestions(false);
    setActiveKeywordSuggestionIndex(-1);
    if (errors.keyword) {
      setErrors((prev) => ({
        ...prev,
        keyword: '',
      }));
    }
  };

  const handleLocationSelect = (location) => {
    setFormData((prev) => ({
      ...prev,
      location: location,
    }));
    setShowLocationSuggestions(false);
    setActiveLocationSuggestionIndex(-1);
    if (errors.location) {
      setErrors((prev) => ({
        ...prev,
        location: '',
      }));
    }
  };

  const handleLocationKeyDown = (e) => {
    if (!showLocationSuggestions || locationSuggestions.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveLocationSuggestionIndex((prev) =>
        prev < locationSuggestions.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveLocationSuggestionIndex((prev) => (prev > 0 ? prev - 1 : -1));
    } else if (e.key === 'Enter' && activeLocationSuggestionIndex >= 0) {
      e.preventDefault();
      handleLocationSelect(locationSuggestions[activeLocationSuggestionIndex]);
    } else if (e.key === 'Escape') {
      setShowLocationSuggestions(false);
      setActiveLocationSuggestionIndex(-1);
    }
  };

  const handleKeywordKeyDown = (e) => {
    if (!showKeywordSuggestions || keywordSuggestions.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveKeywordSuggestionIndex((prev) =>
        prev < keywordSuggestions.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveKeywordSuggestionIndex((prev) => (prev > 0 ? prev - 1 : -1));
    } else if (e.key === 'Enter' && activeKeywordSuggestionIndex >= 0) {
      e.preventDefault();
      handleKeywordSelect(keywordSuggestions[activeKeywordSuggestionIndex]);
    } else if (e.key === 'Escape') {
      setShowKeywordSuggestions(false);
      setActiveKeywordSuggestionIndex(-1);
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.keyword.trim()) {
      newErrors.keyword = 'Keyword is required';
    }

    if (!formData.location.trim()) {
      newErrors.location = 'Location is required';
    }

    // Experience is optional, but if provided must be >= 0
    if (formData.experience !== '' && formData.experience < 0) {
      newErrors.experience = 'Experience must be 0 or more years';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setShowLocationSuggestions(false);
    setShowKeywordSuggestions(false);
    onSearch({
      job_type: formData.job_type || 'internship',
      keyword: formData.keyword.trim(),
      location: formData.location.trim(),
      experience: formData.experience !== '' ? parseInt(formData.experience, 10) : 0,
    });
  };

  return (
    <div className="search-form-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="form-group">
          <label htmlFor="job_type">Job Type</label>
          <select
            id="job_type"
            name="job_type"
            value={formData.job_type}
            onChange={handleChange}
            className="form-control"
            disabled={loading}
          >
            <option value="job">Job</option>
            <option value="internship">Internship</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="keyword">Skills / Designations</label>
          <div className="keyword-input-wrapper" ref={keywordInputRef}>
          <input
            type="text"
            id="keyword"
            name="keyword"
            value={formData.keyword}
            onChange={handleChange}
              onFocus={() => {
                if (keywordSuggestions.length > 0) {
                  setShowKeywordSuggestions(true);
                }
              }}
              onKeyDown={handleKeywordKeyDown}
            placeholder="Skills, Designations, Companies"
            className={`form-control ${errors.keyword ? 'error' : ''}`}
            disabled={loading}
              autoComplete="off"
          />
            {showKeywordSuggestions && keywordSuggestions.length > 0 && (
              <ul className="keyword-suggestions" ref={keywordSuggestionsRef}>
                {keywordSuggestions.map((suggestion, index) => (
                  <li
                    key={index}
                    className={`suggestion-item ${
                      index === activeKeywordSuggestionIndex ? 'active' : ''
                    }`}
                    onClick={() => handleKeywordSelect(suggestion)}
                    onMouseEnter={() => setActiveKeywordSuggestionIndex(index)}
                  >
                    {suggestion}
                  </li>
                ))}
              </ul>
            )}
          </div>
          {errors.keyword && <span className="error-text">{errors.keyword}</span>}
        </div>

        <div className="form-group location-group">
          <label htmlFor="location">Location</label>
          <div className="location-input-wrapper" ref={locationInputRef}>
          <input
            type="text"
            id="location"
            name="location"
            value={formData.location}
            onChange={handleChange}
              onFocus={() => {
                if (locationSuggestions.length > 0) {
                  setShowLocationSuggestions(true);
                }
              }}
              onKeyDown={handleLocationKeyDown}
            placeholder="City, State or Country"
            className={`form-control ${errors.location ? 'error' : ''}`}
            disabled={loading}
              autoComplete="off"
          />
            {showLocationSuggestions && locationSuggestions.length > 0 && (
              <ul className="location-suggestions" ref={locationSuggestionsRef}>
                {locationSuggestions.map((suggestion, index) => (
                  <li
                    key={index}
                    className={`suggestion-item ${
                      index === activeLocationSuggestionIndex ? 'active' : ''
                    }`}
                    onClick={() => handleLocationSelect(suggestion)}
                    onMouseEnter={() => setActiveLocationSuggestionIndex(index)}
                  >
                    {suggestion}
                  </li>
                ))}
              </ul>
            )}
          </div>
          {errors.location && <span className="error-text">{errors.location}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="experience">Experience</label>
          <input
            type="number"
            id="experience"
            name="experience"
            value={formData.experience}
            onChange={handleChange}
            placeholder="Experience"
            min="0"
            className={`form-control ${errors.experience ? 'error' : ''}`}
            disabled={loading}
          />
          {errors.experience && <span className="error-text">{errors.experience}</span>}
        </div>

        <button
          type="submit"
          className="submit-button"
          disabled={loading}
        >
          {loading ? (
            <span className="search-button-loading">
              <span className="search-dot" />
              <span className="search-dot" />
              <span className="search-dot" />
              <span className="search-loading-text">Searching jobs</span>
            </span>
          ) : (
            <span className="search-button-text">Search</span>
          )}
        </button>
      </form>
    </div>
  );
};

export default SearchForm;
