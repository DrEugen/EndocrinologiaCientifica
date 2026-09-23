/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",    // Esto le dice que busque en tus carpetas de Flask
    "./static/**/*.js",         // Por si usas clases en JavaScript
  ],
  safelist: [
    'fixed',
    'bottom-8',
    'right-8',
    'z-50',
    'flex',
    'items-center',
    'justify-center',
    'w-16',
    'h-16',
    'bg-[#25D366]',
    'text-white',
    'rounded-full',
    'shadow-2xl',
    'hover:scale-110',
    'transition-transform',
    'duration-300',
    'animate-bounce',
    //cards testimonios
    'min-w-full',
    'md:min-w-[50%]',
    'lg:min-w-[33.33%]',
    'p-4',
    'transition-opacity',
    'duration-500',
    //Boton WA
    'text-center',
    'bg-green-500',
    'hover:bg-[#208884]',
    'px-8', 
    'py-4',
    'rounded-xl',
    'font-bold',
    'text-lg',
    'shadow-lg',
    'transition-all',
    'transform',
    'hover:-translate-y-1',
    

  ],
  theme: {
    extend: {},
  },
  plugins: [],
}