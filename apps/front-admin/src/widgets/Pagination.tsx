import React from "react";

interface PaginationProps {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
    maxVisiblePages?: number;
    previousLabel?: string;
    nextLabel?: string;
}

export const Pagination: React.FC<PaginationProps> = (
    {
        currentPage,
        totalPages,
        onPageChange,
        maxVisiblePages = 5,
        previousLabel = "Назад",
        nextLabel = "Вперёд",
    }) => {
    const getPaginationPages = () => {
        const pages: (number | string)[] = [];

        if (totalPages <= maxVisiblePages) {
            for (let i = 1; i <= totalPages; i++) pages.push(i);
        } else {
            pages.push(1);
            let startPage = Math.max(2, currentPage - 1);
            let endPage = Math.min(totalPages - 1, currentPage + 1);

            if (currentPage <= 3) endPage = 4;
            else if (currentPage >= totalPages - 2) startPage = totalPages - 3;

            if (startPage > 2) pages.push("...");
            for (let i = startPage; i <= endPage; i++) pages.push(i);
            if (endPage < totalPages - 1) pages.push("...");
            pages.push(totalPages);
        }

        return pages;
    };

    return (
        <div className="pagination_controls">
            <button
                disabled={ currentPage === 1 }
                className="control_btn"
                onClick={ () => onPageChange(currentPage - 1) }
            >
                {previousLabel}
            </button>

            {getPaginationPages().map((pageNumber, index) => (
                <button
                    key={ index }
                    className={ `control_btn ${pageNumber === currentPage ? "active" : ""} ${pageNumber === "..." ? "ellipsis" : ""}` }
                    disabled={ pageNumber === "..." }
                    onClick={ () => typeof pageNumber === "number" && onPageChange(pageNumber) }
                >
                    {pageNumber}
                </button>
            ))}

            <button
                disabled={ currentPage === totalPages }
                className="control_btn"
                onClick={ () => onPageChange(currentPage + 1) }
            >
                {nextLabel}
            </button>
        </div>
    );
};
