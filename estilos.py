# estilos.py
# ES OTRO DESMADRE, MUCHO NO SE USA

TEMA_MEDICO = {
    'color_tema': '#208884',
    'color_secundario': "#5BBFA3",
    'color_terciario': '#006a9b',
    'color_sobre_tema': '#0e96d6',
    'color_claro': '#FEFFFE',      # Fondo/Respiración
    'color_complemento': '#9CDAC8',# Detalles/Bordes
    
    
    #"#a9e4ff"
    # Estilo de las imagenes
    # div_foto: "md:w-1/2 flex justify-center"

    # Configuraciones de Secciones
    'hero': {
        'seccion': 'flex flex-col md:flex-row items-center justify-between py-1 md:py-6 px-4',
        'columnas_flex': 'md:w-1/2 mb-10 md:mb-0',
        'badge': 'inline-block px-4 py-1.5 mb-6 text-xs font-bold tracking-widest uppercase rounded-full text-[#208884] shadow-sm',
        'estilo_foto': "relative w-full h-full rounded-[3rem] overflow-hidden shadow-2xl z-10 border-8 border-white transition-transform duration-700 hover:scale-105"
    },
    
    'confianza': {'seccion_principal': "bg-white py-12 border-y border-gray-100", 
                  'div_principal': "flex flex-wrap justify-around items-center opacity-50 grayscale hover:grayscale-0 transition-all gap-8"},
    

    'servicios': {'seccion_principal': "py-20",
                  'div_encabezado': "text-center mb-16",
                  'h3_servicios': "text-3xl font-bold text-gray-900",
                  'h4_servicios': "text-xl font-bold mb-2",
                  'p_servicios': "text-gray-600",
                  'linea_divisoria': "w-20 h-1 mx-auto mt-4 rounded-full",
                  'div_servicios': "grid grid-cols-1 md:grid-cols-3 gap-8",
                  'cards_servicios': "p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-xl transition-shadow group",
                  'icono_servicio': "text-4xl mb-4 group-hover:scale-110 transition-transform inline-block"},
    
    'contacto': {
        'seccion': "py-20 bg-slate-50",
        'contenedor': "max-w-4xl mx-auto bg-white p-10 rounded-3xl shadow-xl border border-slate-100",
        'titulo': "text-3xl font-bold text-center mb-8",
        'subtitulo': 'max-w-2xl mx-auto text-ml text-center text-gray-500 mb-8 ',
        'label': "block text-sm font-semibold text-gray-700 mb-2",
        'input': "w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-[#0ea5e9] focus:outline-none mb-6",
        'boton_enviar': "w-full bg-[#0ea5e9] text-white font-bold py-4 rounded-xl hover:bg-[#0b7db2] transition-all shadow-lg"
    },

    'testimonios': {
        'seccion': "py-20 bg-white overflow-hidden",
        'contenedor': "relative after:absolute after:top-0 after:right-0 after:h-full after:w-12 after:bg-gradient-to-l after:from-white after:to-transparent before:absolute before:top-0 before:left-0 before:h-full before:w-12 before:bg-gradient-to-r before:from-white before:to-transparent before:z-10 after:z-10",
        'titulo': "text-3xl font-bold text-center mb-12",
        'card': "min-w-full md:min-w-[50%] lg:min-w-[33.33%] p-4 transition-opacity duration-500",
        'burbuja': "p-8 rounded-3xl relative shadow-lg",
        #'garantia_box': "mt-10 p-6 bg-amber-50 border-2 border-dashed border-amber-200 rounded-2xl flex items-start gap-4",
        'texto': "text-slate-600 italic mb-6 leading-relaxed",
        'autor': "font-bold text-slate-900",
        'puesto': "text-sm text-slate-500",
        'controles': "flex justify-center gap-4 mt-10",
        'boton_slider': "p-3 rounded-full transition"    
        },

    'beneficios': {
        'grid': "grid grid-cols-1 md:grid-cols-2 gap-12 items-center",
        'lista': "space-y-4",
        'item': "flex items-center gap-3 text-lg",
        'check': "text-white text-[36px]"
    },
    
    'oferta': {
        
        'contenedor': "max-w-4xl mx-auto rounded-3xl shadow-2xl overflow-hidden border-2",
        'header': "p-8 text-center",
        'pre_titulo': 'uppercase tracking-widest text-sm font-bold opacity-80',
        'titulo': 'text-3xl md:text-4xl font-extrabold mt-2',
        'cuerpo': "p-10",
        'grid': 'grid grid-cols-1 md:grid-cols-2 gap-x-12 mb-10',
        'item_lista': "flex items-center gap-4 py-4 border-b last:border-0",
        'check_icono': "text-xl font-bold",
        'garantia_box': "mt-10 p-6 bg-amber-50 border-2 border-dashed border-amber-200 rounded-2xl flex items-start gap-4",
        'est_limite': 'mt-12 text-center',
        'escala_boton': 'flex justify-center transform hover:scale-105 transition-transform duration-300'
    },

    'autoridad': {
        'seccion': "py-24",
        'titulo': 'text-4xl font-bold mt-4 mb-6',
        'texto': 'text-lg text-slate-600 mb-8 leading-relaxed',
        'grid': "grid grid-cols-1 lg:grid-cols-2 gap-16 items-center",
        'foto_contenedor': "relative rounded-2xl overflow-hidden shadow-2xl",
        'gradiente': 'absolute bottom-0 left-0 right-0 p-8 bg-gradient-to-t from-slate-900 to-transparent',
        'stats_grid': "grid grid-cols-2 gap-6 mt-8",
        'stat_card': "p-6 rounded-xl border-b-4",
        'stat_numero': "block text-3xl font-bold",
        'stat_etiqueta': "text-sm uppercase tracking-wide",
        'cert_lista': "flex flex-wrap gap-3 mt-6",
        'cert_badge': "px-3 py-1 rounded-md text-xs font-bold border"
    },

    'footer': {
        #'color_bg': "#0b7db2",
        #'color_bg': '#006a9b',
        'color_texto': '#111111'
    },

    'texto_fuerte': 'text-slate-900',
    'texto_s_fuerte': 'text-slate-800',
    'texto_medio_fuerte': 'text-slate-700',
    'texto_medio': 'text-slate-600',
    'texto_medio_debil': 'text-slate-500',
    'texto_debil': 'text-slate-300',
    'texto_muy_debil': 'text-slate-200',
    'texto_sintoma': 'text-red-600',
    'texto_claro': 'text-white',

    'bg_claro': 'white',
    'bg_debil': 'slate-50',
    'bg_suave': 'slate-100',
    'bg_medio': 'slate-200',
    'bg_fuerte': 'slate-900',

    'borde_debil': '[#9CDAC8]/10',
    'borde_debil_medio': 'slate-200',

    'sub_contenedor': "max-w-6xl mx-auto px-4",
    'pre_titulo': 'font-bold uppercase tracking-widest text-sm',
    'h2': 'text-4xl md:text-6xl font-extrabold leading-tight mb-6',
    'leyenda_texto': 'border-l-4 p-6 text-left inline-block',
    'p': 'mb-8 leading-relaxed',
    'card': 'bg-white p-8 rounded-2xl border border-blue-50 shadow-sm hover:shadow-blue-100',
    'boton_primario': 'text-white px-8 py-4 rounded-xl font-bold shadow-lg transition-all',
    'boton_normal': "text-center border-2 border-gray-300 text-gray-700 px-8 py-4 rounded-xl font-bold text-lg hover:bg-gray-100 transition-all",
    'boton_whatsapp': "text-center bg-green-500 hover:bg-[#208884] text-white px-8 py-4 rounded-xl font-bold text-lg shadow-lg transition-all transform hover:-translate-y-1",
    'whatsapp_flotante': "fixed bottom-8 right-8 z-50 flex items-center justify-center w-16 h-16 bg-[#25D366] text-white rounded-full shadow-2xl hover:scale-110 transition-transform duration-300 animate-bounce"
}

