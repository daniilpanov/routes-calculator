import { useState, useRef, useEffect } from "react";

interface DropdownProps {
    options: string[];
    selected: string;
    placeholder?: string;
    onSelect: (option: string) => void;
    className?: string;
}

export const Dropdown = (
    {
        options,
        selected,
        onSelect,
        placeholder = "",
        className = "",
    }: DropdownProps) => {
    const [ isOpen, setIsOpen ] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node))
                setIsOpen(false);
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () =>
            document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleSelect = (option: string) => {
        onSelect(option);
        setIsOpen(false);
    };

    return (
        <div className={ `dropdown-container ${className}` } ref={ dropdownRef }>
            <button
                className="dropdown-toggle"
                onClick={ () => setIsOpen(!isOpen) }
                type="button"
            >
                {selected || placeholder}
            </button>

            {isOpen && (
                <div className="dropdown-menu">
                    {options.map((option, index) => (
                        <div
                            key={ index }
                            className="dropdown-item"
                            onClick={ () => handleSelect(option) }
                        >
                            {option}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
