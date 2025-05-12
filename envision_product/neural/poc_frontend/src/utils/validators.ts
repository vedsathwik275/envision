/**
 * Check if a file is valid CSV
 */
export const isValidCsvFile = (file: File): boolean => {
  // Check file type
  const validTypes = ['text/csv', 'application/vnd.ms-excel', 'application/csv'];
  if (!validTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.csv')) {
    return false;
  }
  
  // Check file size (limit to 10MB)
  const maxSize = 10 * 1024 * 1024; // 10MB in bytes
  if (file.size > maxSize) {
    return false;
  }
  
  return true;
};

/**
 * Validate the presence of required columns in data
 */
export const hasRequiredColumns = (columns: string[], requiredColumns: string[]): boolean => {
  return requiredColumns.every(col => columns.includes(col));
};

/**
 * Check if columns are in the expected format for the order volume prediction model
 */
export const isValidForOrderVolumeModel = (columns: string[]): boolean => {
  const requiredColumns = [
    'SOURCE CITY',
    'DESTINATION CITY',
    'ORDER TYPE',
    'ORDER MONTH',
    'ORDER VOLUME'
  ];
  
  return hasRequiredColumns(columns, requiredColumns);
};

/**
 * Validate a file against a model's requirements
 */
export const validateFileForModel = (
  columns: string[],
  modelId: string
): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  // Order volume model validation
  if (modelId === 'order-volume') {
    if (!isValidForOrderVolumeModel(columns)) {
      errors.push('File is missing required columns for order volume prediction.');
      errors.push('Required columns: SOURCE CITY, DESTINATION CITY, ORDER TYPE, ORDER MONTH, ORDER VOLUME');
    }
  } else {
    // Add validations for other models here
    errors.push('Unknown model type.');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
}; 