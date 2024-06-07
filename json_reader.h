#ifndef JSON_READER_H
#define JSON_READER_H

typedef struct {
    char *order;
    char *pseudo;
    int port;
} JSON_Message;


JSON_Message lire_json(const char *json_string);
int is_valid_json(const char *json_string);
char *add_attribute_to_json(const char *original_json, const char *key, const char *value);
void remove_attribute_from_json(const char *json_string, const char *key);

#endif /* JSON_READER_H */
