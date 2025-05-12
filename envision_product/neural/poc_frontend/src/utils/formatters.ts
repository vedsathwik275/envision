/**
 * Format a number as a percentage
 */
export const formatPercentage = (value: number): string => {
  return `${Math.round(value)}%`;
};

/**
 * Format a number with commas for thousands
 */
export const formatNumber = (value: number): string => {
  if (value === undefined || value === null) return '';
  
  return new Intl.NumberFormat().format(value);
};

/**
 * Format a timestamp as a readable date and time
 */
export const formatDateTime = (timestamp: string): string => {
  const date = new Date(timestamp);
  return date.toLocaleString();
};

/**
 * Format a file size in bytes to a human-readable format
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Format seconds into minutes and seconds
 */
export const formatTimeRemaining = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.round(seconds % 60);
  
  if (minutes === 0) {
    return `${remainingSeconds}s`;
  }
  
  return `${minutes}m ${remainingSeconds}s`;
};

/**
 * Format a month number (1-12) to a month name
 */
export const formatMonthName = (month: number): string => {
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  
  return months[month - 1] || '';
};

/**
 * Format a date string in the format 'YYYY-MM' to a more readable format
 */
export const formatYearMonth = (dateString: string): string => {
  if (!dateString) return '';
  
  try {
    const [year, month] = dateString.split('-');
    const date = new Date(parseInt(year), parseInt(month) - 1);
    
    return date.toLocaleString('default', { month: 'long', year: 'numeric' });
  } catch (error) {
    console.error('Error formatting date:', error);
    return dateString; // Return original string if parsing fails
  }
}; 