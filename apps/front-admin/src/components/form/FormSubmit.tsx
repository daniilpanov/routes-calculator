import React from "react";

interface FormSubmitProps {
    children: React.ReactNode;
    type?: "button" | "submit" | "reset";
    className?: string;
    disabled?: boolean
    onclick?: () => void;
}

export default function FormSubmit({ children, type = "submit", className, disabled, onclick }: FormSubmitProps) {
    return (
        <button type={ type } className={ className } disabled={ disabled } onClick={ onclick }>
            {children}
        </button>
    );
}
