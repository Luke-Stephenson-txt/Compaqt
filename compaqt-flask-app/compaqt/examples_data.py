# Detailed examples data for the examples page

EXAMPLES = [
    {
        'id': 'c-parser-enhancement',
        'name': 'C Parser Enhancement',
        'description': 'Adding hex color parsing support to a .pres file parser',
        'before_tokens': 17761,
        'after_tokens': 14151,
        'files': 6,

        # Detailed benchmark data
        'question': {
            'title': 'Add support for parsing hex color values in addition to vec4 RGBA format',
            'problem': '''Currently, the .pres file parser only supports RGBA colors in the vec4{r, g, b, a} format. Users want to also be able to specify colors using hex format like #FF00FF or #FF00FF80 (with optional alpha). The parser should:
- Detect hex color format when parsing color fields (e.g., fill_col, col, outline_col)
- Convert hex values to vec4d format internally
- Support both 6-digit (#RRGGBB) and 8-digit (#RRGGBBAA) hex formats
- Maintain backward compatibility with existing vec4{} syntax'''
        },

        'metrics': {
            'original_tokens': 17761,
            'packed_tokens': 14151,
            'savings_percent': 20.3,
            'compression_ratio': '1.26x',
            'files_available': 6,
            'files_included': 6,
            'inclusion_rate': 100.0,
        },

        'cost_analysis': {
            'input_price_per_million': 0.15,
            'output_price_per_million': 0.60,
            'original_input_cost': 0.002664,
            'packed_input_cost': 0.002123,
            'input_savings': 0.000541,
            'output_tokens': 1000,
        },

        'file_details': [
            {
                'name': 'app_pres_parse.c',
                'path': 'src/app/src/app/app_pres_parse.c',
                'relevance': 0.95,
                'description': 'Main parser implementation',
                'original': '''#include "app/app_pres.h"

#include <ctype.h>

typedef struct {
    b32 valid;
    string8 file;
    u64 pos;
    u64 line;
} pres_parser;

static void parse_next_char_noc(pres_parser* parser);
static void parse_next_char(pres_parser* parser);
static void parse_syntax_error(pres_parser* parser);
static void parse_settings(marena* arena, app_app* app, pres_parser* parser);
static void parse_plugins(marena* arena, marena_temp scratch, app_app* app,
                          app_pres* pres, pres_parser* parser);
static void parse_slides(marena* arena, marena_temp scratch, app_app* app,
                         app_pres* pres, pres_parser* parser);
static void parse_slide(marena* arena, marena_temp scratch, app_app* app,
                        app_pres* pres, app_slide_node* slide, pres_parser* parser);
static void parse_anim(marena* arena, marena_temp scratch, app_anim* anim,
                       pres_parser* parser);
static field_val parse_field(marena* arena, marena_temp scratch, pres_parser* parser);
static field_val parse_arr(marena* arena, marena_temp sratch, pres_parser* parser);
static field_val parse_vec(pres_parser* parser);
static f64 parse_f64(pres_parser* parser);
static string8 parse_string(marena* arena, pres_parser* parser);
static string8 parse_keyword(pres_parser* parser);

#define P_CHAR(p) ((p)->file.str[(p)->pos])
#define P_WHITESPACE(p) ((p)->file.str[(p)->pos] == ' '  || \\
                         (p)->file.str[(p)->pos] == '\\t' || \\
                         (p)->file.str[(p)->pos] == '\\n' || \\
                         (p)->file.str[(p)->pos] == '\\r')
#define P_SKIP_SPACE(p) while (P_WHITESPACE((p))) { parse_next_char((p)); }
#define P_KEY_CHAR(p) (isalnum((p)->file.str[(p)->pos]) || \\
                       (p)->file.str[(p)->pos] == '_')

app_pres* app_pres_parse(marena* arena, app_app* app, string8 file_path) {
    app_pres* pres = CREATE_ZERO_STRUCT(arena, app_pres);
    pres->obj_reg = obj_reg_create(arena, PRES_MAX_DESCS);

    app->pres = pres;

    marena_temp scratch = marena_scratch_get(&arena, 1);
    string8 file = os_file_read(scratch.arena, file_path);

    // ... continues for 800+ more lines ...''',
                'compressed': '''#include "app/app_pres.h"
#include <ctype.h>
typedef struct{b32 valid;string8 file;u64 pos;u64 line;}pres_parser;static void parse_next_char_noc(pres_parser*parser);static void parse_next_char(pres_parser*parser);static void parse_syntax_error(pres_parser*parser);static void parse_settings(marena*arena,app_app*app,pres_parser*parser);static void parse_plugins(marena*arena,marena_temp scratch,app_app*app,app_pres*pres,pres_parser*parser);static void parse_slides(marena*arena,marena_temp scratch,app_app*app,app_pres*pres,pres_parser*parser);static void parse_slide(marena*arena,marena_temp scratch,app_app*app,app_pres*pres,app_slide_node*slide,pres_parser*parser);static void parse_anim(marena*arena,marena_temp scratch,app_anim*anim,pres_parser*parser);static field_val parse_field(marena*arena,marena_temp scratch,pres_parser*parser);static field_val parse_arr(marena*arena,marena_temp sratch,pres_parser*parser);static field_val parse_vec(pres_parser*parser);static f64 parse_f64(pres_parser*parser);static string8 parse_string(marena*arena,pres_parser*parser);static string8 parse_keyword(pres_parser*parser);
#define P_CHAR(p) ((p)->file.str[(p)->pos])
#define P_WHITESPACE(p) ((p)->file.str[(p)->pos] == ' '  || (p)->file.str[(p)->pos] == '\\t' || (p)->file.str[(p)->pos] == '\\n' || (p)->file.str[(p)->pos] == '\\r')
#define P_SKIP_SPACE(p) while (P_WHITESPACE((p))) { parse_next_char((p)); }
#define P_KEY_CHAR(p) (isalnum((p)->file.str[(p)->pos]) || (p)->file.str[(p)->pos] == '_')
app_pres*app_pres_parse(marena*arena,app_app*app,string8 file_path){app_pres*pres=CREATE_ZERO_STRUCT(arena,app_pres);pres->obj_reg=obj_reg_create(arena,PRES_MAX_DESCS);app->pres=pres;marena_temp scratch=marena_scratch_get(&arena,1);string8 file=os_file_read(scratch.arena,file_path);'''
            },
            {
                'name': 'app_pres.h',
                'path': 'src/app/include/app/app_pres.h',
                'relevance': 0.85,
                'description': 'Presentation header definitions',
                'original': '''#ifndef APP_PRES_H
#define APP_PRES_H

#ifdef __cplusplus
extern "C" {
#endif

#include "base/base.h"
#include "os/os.h"
#include "app_app.h"
#include "app_anim.h"
#include "app_obj_pool.h"

#define PRES_MAX_OBJS 64
#define PRES_MAX_ANIMS (PRES_MAX_OBJS * 2)

typedef struct app_slide_node {
    struct app_slide_node* next;
    struct app_slide_node* prev;

    app_obj_pool* objs;
    app_anim_pool* anims;
} app_slide_node;

typedef struct app_pres {
    u32 num_plugins;
    os_library* plugins;

    obj_register* obj_reg;

    app_slide_node* first_slide;
    app_slide_node* last_slide;
    u32 num_slides;
    u32 slide_index;
    app_slide_node* cur_slide;

    app_slide_node* global_slide;
} app_pres;

#define PRES_MAX_DESCS 32

app_pres* app_pres_parse(marena* arena, app_app* app, string8 file_path);
void app_pres_destroy(app_pres* pres);
void app_pres_next_slide(app_pres* pres);
void app_pres_prev_slide(app_pres* pres);
void app_pres_draw(app_pres* pres, app_app* app);
void app_pres_update(app_pres* pres, app_app* app, f32 delta);

#ifdef __cplusplus
}
#endif

#endif // APP_PRES_H''',
                'compressed': '''#ifndef APP_PRES_H
#define APP_PRES_H
#ifdef __cplusplus
extern"C"{#endif
#include "base/base.h"
#include "os/os.h"
#include "app_app.h"
#include "app_anim.h"
#include "app_obj_pool.h"
#define PRES_MAX_OBJS 64
#define PRES_MAX_ANIMS (PRES_MAX_OBJS * 2)
typedef struct app_slide_node{struct app_slide_node*next;struct app_slide_node*prev;app_obj_pool*objs;app_anim_pool*anims;}app_slide_node;typedef struct app_pres{u32 num_plugins;os_library*plugins;obj_register*obj_reg;app_slide_node*first_slide;app_slide_node*last_slide;u32 num_slides;u32 slide_index;app_slide_node*cur_slide;app_slide_node*global_slide;}app_pres;#define PRES_MAX_DESCS 32
app_pres*app_pres_parse(marena*arena,app_app*app,string8 file_path);void app_pres_destroy(app_pres*pres);void app_pres_next_slide(app_pres*pres);void app_pres_prev_slide(app_pres*pres);void app_pres_draw(app_pres*pres,app_app*app);void app_pres_update(app_pres*pres,app_app*app,f32 delta);#ifdef __cplusplus
}#endif
#endif // APP_PRES_H'''
            },
            {
                'name': 'base_str.h',
                'path': 'src/core/include/base/base_str.h',
                'relevance': 0.75,
                'description': 'String utilities header',
                'original': '''#ifndef BASE_STR_H
#define BASE_STR_H

#ifdef __cplusplus
extern "C" {
#endif

#include <string.h>
#include <stdio.h>
#include <stdarg.h>

#include "base_defs.h"
#include "base_mem.h"

typedef struct {
    u8* str;
    u64 size;
} string8;

typedef struct {
    u16* str;
    u64 size;
} string16;

typedef struct {
    u32* str;
    u64 size;
} string32;

typedef struct string8_node {
    struct string8_node* next;
    string8 str;
} string8_node;

typedef struct {
    string8_node* first;
    string8_node* last;
    u64 node_count;
    u64 total_size;
} string8_list;

#define STR8_LIT(s) ((string8){ (u8*)(s), sizeof(s)-1 })
#define STR(s) STR8_LIT(s)

// ... function declarations continue ...''',
                'compressed': '''#ifndef BASE_STR_H
#define BASE_STR_H
#ifdef __cplusplus
extern"C"{#endif
#include <string.h>
#include <stdio.h>
#include <stdarg.h>
#include "base_defs.h"
#include "base_mem.h"
typedef struct{u8*str;u64 size;}string8;typedef struct{u16*str;u64 size;}string16;typedef struct{u32*str;u64 size;}string32;typedef struct string8_node{struct string8_node*next;string8 str;}string8_node;typedef struct{string8_node*first;string8_node*last;u64 node_count;u64 total_size;}string8_list;
#define STR8_LIT(s) ((string8){ (u8*)(s), sizeof(s)-1 })
#define STR(s) STR8_LIT(s)'''
            },
            {
                'name': 'base_str.c',
                'path': 'src/core/src/base/base_str.c',
                'relevance': 0.70,
                'description': 'String utilities implementation',
                'original': '''#include "base/base_str.h"
#include "base/base_log.h"

string8 str8_create(u8* str, u64 size) {
    return (string8) { str, size };
}

string8 str8_from_range(u8* start, u8* end) {
    return (string8) { start, (u64)(end - start) };
}

string8 str8_from_cstr(u8* cstr) {
    u8* ptr = cstr;
    for (; *ptr != 0; ptr += 1);
    return str8_from_range(cstr, ptr);
}

string8 str8_copy(marena* arena, string8 str) {
    string8 out = {
        .str = (u8*)marena_push(arena, str.size),
        .size = str.size
    };
    memcpy(out.str, str.str, str.size);
    return out;
}

b8 str8_equals(string8 a, string8 b) {
    if (a.size != b.size) return false;
    for (u64 i = 0; i < a.size; i++) {
        if (a.str[i] != b.str[i]) return false;
    }
    return true;
}

// ... more functions continue ...''',
                'compressed': '''#include "base/base_str.h"
#include "base/base_log.h"
string8 str8_create(u8*str,u64 size){return(string8){str,size};}string8 str8_from_range(u8*start,u8*end){return(string8){start,(u64)(end-start)};}string8 str8_from_cstr(u8*cstr){u8*ptr=cstr;for(;*ptr!=0;ptr+=1);return str8_from_range(cstr,ptr);}string8 str8_copy(marena*arena,string8 str){string8 out={.str=(u8*)marena_push(arena,str.size),.size=str.size};memcpy(out.str,str.str,str.size);return out;}b8 str8_equals(string8 a,string8 b){if(a.size!=b.size)return false;for(u64 i=0;i<a.size;i++){if(a.str[i]!=b.str[i])return false;}return true;}'''
            },
            {
                'name': 'rectangle_obj.c',
                'path': 'plugins/basic/rectangle_obj.c',
                'relevance': 0.60,
                'description': 'Rectangle object with color fields',
                'original': '''#include "plugin.h"

typedef struct {
    f64 x, y;
    f64 w, h;

    b32 fill;
    vec4d fill_col;

    b32 outline;
    vec4d outline_col;
    f64 outline_width;
} pres_rect;

void rect_default(marena* arena, app_app* app, void* obj) {
    AP_UNUSED(arena);
    AP_UNUSED(app);

    pres_rect* r = (pres_rect*)obj;
    *r = (pres_rect) {
        .fill = true,
        .fill_col = (vec4d){ 1, 1, 1, 1 },
        .outline_width = 2,
        .outline_col = (vec4d){ 1, 1, 1, 1 }
    };
}

void rect_draw(app_app* app, void* obj) {
    pres_rect* r = (pres_rect*)obj;

    if (r->fill) {
        f64 w = r->outline ? r->outline_width : 0;
        draw_rectb_push(app->rectb, (rect){
            (f32)r->x + w, (f32)r->y + w,
            (f32)r->w - w - w, (f32)r->h - w - w
        }, r->fill_col);
    }

    if (r->outline) {
        // Draw outline rectangles...
    }
}''',
                'compressed': '''#include "plugin.h"
typedef struct{f64 x,y;f64 w,h;b32 fill;vec4d fill_col;b32 outline;vec4d outline_col;f64 outline_width;}pres_rect;void rect_default(marena*arena,app_app*app,void*obj){AP_UNUSED(arena);AP_UNUSED(app);pres_rect*r=(pres_rect*)obj;*r=(pres_rect){.fill=true,.fill_col=(vec4d){1,1,1,1},.outline_width=2,.outline_col=(vec4d){1,1,1,1}};}void rect_draw(app_app*app,void*obj){pres_rect*r=(pres_rect*)obj;if(r->fill){f64 w=r->outline?r->outline_width:0;draw_rectb_push(app->rectb,(rect){(f32)r->x+w,(f32)r->y+w,(f32)r->w-w-w,(f32)r->h-w-w},r->fill_col);}if(r->outline){}}'''
            },
            {
                'name': 'plugin_text.c',
                'path': 'plugins/text/plugin_text.c',
                'relevance': 0.55,
                'description': 'Text plugin with color support',
                'original': '''#include "ap_core.h"
#include "app/app.h"
#include "stb_rect_pack.h"
#include "stb_truetype.h"

typedef struct {
    u32 face;
    u32 font;
} font_ref;

typedef struct {
    string8 source;
    struct {
        u64 size;
        f64* data;
    } sizes;
    b32 is_default;
} pres_font;

typedef struct {
    string8 text;
    string8 font_name;
    f64 font_size;
    f64 x, y;
    b32 center_x, center_y;
    vec4d col;  // Color field that needs hex support
    font_ref font;
} pres_text;

#define MAX_FACES 8
#define MAX_FONTS 8
#define NUM_CHARS 95

// ... plugin implementation continues ...''',
                'compressed': '''#include "ap_core.h"
#include "app/app.h"
#include "stb_rect_pack.h"
#include "stb_truetype.h"
typedef struct{u32 face;u32 font;}font_ref;typedef struct{string8 source;struct{u64 size;f64*data;}sizes;b32 is_default;}pres_font;typedef struct{string8 text;string8 font_name;f64 font_size;f64 x,y;b32 center_x,center_y;vec4d col;font_ref font;}pres_text;#define MAX_FACES 8
#define MAX_FONTS 8
#define NUM_CHARS 95'''
            },
        ],
    },
    {
        'id': 'data-processing-pipeline',
        'name': 'Data Processing Pipeline',
        'description': 'Python data processing scripts with data cleaning and analysis',
        'before_tokens': 9876,
        'after_tokens': 5234,
        'files': 8,
        'question': {
            'title': 'Sample Data Pipeline Task',
            'problem': 'This is a placeholder example. Add your own benchmark data.'
        },
        'metrics': {
            'original_tokens': 9876,
            'packed_tokens': 5234,
            'savings_percent': 47.0,
            'compression_ratio': '1.89x',
            'files_available': 8,
            'files_included': 8,
            'inclusion_rate': 100.0,
        },
        'cost_analysis': {
            'input_price_per_million': 0.15,
            'output_price_per_million': 0.60,
            'original_input_cost': 0.001481,
            'packed_input_cost': 0.000785,
            'input_savings': 0.000696,
            'output_tokens': 800,
        },
        'files': [],
    },
    {
        'id': 'api-microservices',
        'name': 'API Microservices',
        'description': 'RESTful API services with authentication and database connections',
        'before_tokens': 12456,
        'after_tokens': 7654,
        'files': 15,
        'question': {
            'title': 'Sample API Task',
            'problem': 'This is a placeholder example. Add your own benchmark data.'
        },
        'metrics': {
            'original_tokens': 12456,
            'packed_tokens': 7654,
            'savings_percent': 38.5,
            'compression_ratio': '1.63x',
            'files_available': 15,
            'files_included': 15,
            'inclusion_rate': 100.0,
        },
        'cost_analysis': {
            'input_price_per_million': 0.15,
            'output_price_per_million': 0.60,
            'original_input_cost': 0.001868,
            'packed_input_cost': 0.001148,
            'input_savings': 0.000720,
            'output_tokens': 900,
        },
        'files': [],
    },
    {
        'id': 'machine-learning-models',
        'name': 'Machine Learning Models',
        'description': 'ML model training and inference code with preprocessing',
        'before_tokens': 18345,
        'after_tokens': 10234,
        'files': 10,
        'question': {
            'title': 'Sample ML Task',
            'problem': 'This is a placeholder example. Add your own benchmark data.'
        },
        'metrics': {
            'original_tokens': 18345,
            'packed_tokens': 10234,
            'savings_percent': 44.2,
            'compression_ratio': '1.79x',
            'files_available': 10,
            'files_included': 10,
            'inclusion_rate': 100.0,
        },
        'cost_analysis': {
            'input_price_per_million': 0.15,
            'output_price_per_million': 0.60,
            'original_input_cost': 0.002752,
            'packed_input_cost': 0.001535,
            'input_savings': 0.001217,
            'output_tokens': 1200,
        },
        'files': [],
    },
]

def get_example_by_id(example_id):
    """Get an example by its ID."""
    for example in EXAMPLES:
        if example['id'] == example_id:
            return example
    return None

def get_all_examples():
    """Get basic info for all examples (for the grid view)."""
    return [{
        'id': e['id'],
        'name': e['name'],
        'description': e['description'],
        'before_tokens': e['before_tokens'],
        'after_tokens': e['after_tokens'],
        'files': e['files'],
    } for e in EXAMPLES]
