import React from "react";

interface FormInputProps {
    type: string;
    name: string;
    value: string;
    placeholder: string;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    required?: boolean;
    className?: string;
}

export default function FormInput({ type, name, value, placeholder, onChange, required = false, className }: FormInputProps) {
    return (
        <input
            type={ type }
            name={ name }
            value={ value }
            placeholder={ placeholder }
            onChange={ onChange }
            required={ required }
            className={ className }
        />
    );
}
