import React from "react";

interface FormSubmitProps {
    children: React.ReactNode;
    type?: "button" | "submit" | "reset";
    className?: string;
    disabled?: boolean;
}

export default function FormSubmit({ children, type = "submit", className, disabled }: FormSubmitProps) {
    return (
        <button type={ type } className={ className } disabled={ disabled }>
            {children}
        </button>
    );
}
