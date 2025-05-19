
import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";

interface Column {
  name: string;
  type: string;
  statistics?: {
    min?: number | string;
    max?: number | string;
    mean?: number;
    nullCount?: number;
    uniqueCount?: number;
  };
}

interface DataPreviewProps {
  columns: Column[];
  rows: Record<string, any>[];
  totalRows: number;
  fileName: string;
  loading?: boolean;
}

export function DataPreview({
  columns,
  rows,
  totalRows,
  fileName,
  loading = false
}: DataPreviewProps) {
  const [page, setPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const pageCount = Math.ceil(totalRows / rowsPerPage);
  
  const getDataType = (type: string) => {
    switch (type.toLowerCase()) {
      case "number":
      case "int":
      case "float":
      case "double":
        return "Number";
      case "string":
      case "text":
        return "Text";
      case "date":
      case "datetime":
        return "Date";
      case "boolean":
      case "bool":
        return "Boolean";
      default:
        return type;
    }
  };
  
  const getTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "number":
      case "int":
      case "float":
      case "double":
        return "bg-blue-100 text-blue-800";
      case "string":
      case "text":
        return "bg-green-100 text-green-800";
      case "date":
      case "datetime":
        return "bg-purple-100 text-purple-800";
      case "boolean":
      case "bool":
        return "bg-amber-100 text-amber-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };
  
  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Loading data preview...</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-6 bg-muted rounded w-1/3"></div>
            <div className="space-y-2">
              <div className="h-4 bg-muted rounded"></div>
              <div className="h-4 bg-muted rounded"></div>
              <div className="h-4 bg-muted rounded"></div>
              <div className="h-4 bg-muted rounded"></div>
              <div className="h-4 bg-muted rounded"></div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Data Preview: {fileName}</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">
            {totalRows} rows • {columns.length} columns
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Rows per page:</span>
            <Select value={rowsPerPage.toString()} onValueChange={(value) => setRowsPerPage(parseInt(value))}>
              <SelectTrigger className="w-20">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="10">10</SelectItem>
                <SelectItem value="25">25</SelectItem>
                <SelectItem value="50">50</SelectItem>
                <SelectItem value="100">100</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                {columns.map((column) => (
                  <TableHead key={column.name} className="whitespace-nowrap">
                    <div className="flex flex-col">
                      <div className="font-medium">{column.name}</div>
                      <Badge variant="outline" className={getTypeColor(column.type)}>
                        {getDataType(column.type)}
                      </Badge>
                    </div>
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map((row, rowIndex) => (
                <TableRow key={rowIndex}>
                  {columns.map((column) => (
                    <TableCell key={`${rowIndex}-${column.name}`} className="overflow-hidden text-ellipsis max-w-[200px]">
                      {row[column.name]?.toString() || "-"}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        
        {/* Pagination */}
        {pageCount > 1 && (
          <div className="flex items-center justify-between py-4">
            <p className="text-sm text-muted-foreground">
              Showing {(page - 1) * rowsPerPage + 1} to{" "}
              {Math.min(page * rowsPerPage, totalRows)} of {totalRows} entries
            </p>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
                disabled={page === 1}
              >
                Previous
              </Button>
              {Array.from({ length: Math.min(5, pageCount) }, (_, i) => {
                const pageNumber = i + 1;
                return (
                  <Button
                    key={i}
                    variant={pageNumber === page ? "default" : "outline"}
                    size="sm"
                    onClick={() => setPage(pageNumber)}
                  >
                    {pageNumber}
                  </Button>
                );
              })}
              {pageCount > 5 && <span className="text-muted-foreground">...</span>}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((prev) => Math.min(prev + 1, pageCount))}
                disabled={page === pageCount}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
