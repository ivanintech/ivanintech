'use client';

import { motion } from 'framer-motion';
import type { HTMLMotionProps } from 'framer-motion';

interface AnimatedSectionProps extends HTMLMotionProps<"div"> {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  once?: boolean; // Controla si la animación solo ocurre una vez
}

export function AnimatedSection({ 
  children, 
  className, 
  delay = 0, 
  once = true, // Por defecto, animar solo una vez
  ...rest // Pasar otras props de motion.div si es necesario
}: AnimatedSectionProps) {
  const variants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once: once, amount: 0.2 }} // Animar cuando el 20% sea visible
      transition={{ duration: 0.6, delay: delay, ease: "easeOut" }}
      variants={variants}
      className={className}
      {...rest}
    >
      {children}
    </motion.div>
  );
} 