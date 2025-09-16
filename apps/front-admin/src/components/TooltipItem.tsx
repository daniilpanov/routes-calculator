import React, { ReactNode } from "react";
import "../resources/scss/components/Tooltip.scss";

interface TooltipItemProps {
    label: string;
    children: ReactNode;
    onClick?: () => void;
}

export function TooltipItem({ label, children, onClick }: TooltipItemProps) {
    return (
        <div className="tooltip_container" onClick={ onClick }>
            <span className="tooltip_word">{label}</span>
            <div className="tooltip_content">{children}</div>
        </div>
    );
}
