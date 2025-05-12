/**
 * Delay function for simulating API calls in development
 */
export const delay = (ms: number): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

/**
 * Get a unique id
 */
export const generateId = (): string => {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
};

/**
 * Group an array of objects by a key
 */
export const groupBy = <T>(array: T[], key: keyof T): Record<string, T[]> => {
  return array.reduce((result, item) => {
    const groupKey = String(item[key]);
    if (!result[groupKey]) {
      result[groupKey] = [];
    }
    result[groupKey].push(item);
    return result;
  }, {} as Record<string, T[]>);
};

/**
 * Deep clone an object
 */
export const deepClone = <T>(obj: T): T => {
  return JSON.parse(JSON.stringify(obj));
};

/**
 * Parse CSV string into a 2D array
 */
export const parseCSV = (csvString: string): string[][] => {
  // Simple CSV parser - for more complex CSVs, use a library
  const rows = csvString.split('\n');
  return rows.map(row => row.split(',').map(cell => cell.trim()));
};

/**
 * Convert first 10 rows of CSV file to a string
 */
export const previewCSVFile = async (file: File): Promise<string[][]> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (e: ProgressEvent<FileReader>) => {
      try {
        const contents = e.target?.result as string;
        const rows = contents.split('\n');
        const preview = rows.slice(0, 11).map(row => row.split(',').map(cell => cell.trim()));
        resolve(preview);
      } catch (error) {
        reject(error);
      }
    };
    
    reader.onerror = () => {
      reject(new Error('Error reading file'));
    };
    
    reader.readAsText(file);
  });
}; 