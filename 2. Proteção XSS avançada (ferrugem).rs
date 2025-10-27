use ammonia::{Builder, UrlRelative};
use serde::Serialize;
use std::borrow::Cow;

#[derive(Clone)]
pub struct HtmlSanitizer {
    cleaner: Builder<'static>,
}

impl HtmlSanitizer {
    pub fn new() -> Self {
        let mut cleaner = Builder::default();
        
        // Configure HTML sanitization rules
        cleaner.tags(hashset![
            "p", "br", "ul", "ol", "li", "h1", "h2", "h3",
            "h4", "h5", "h6", "pre", "code", "strong", "em",
            "a", "img", "blockquote"
        ]);
        
        cleaner.tag_attributes(hashmap![
            "a" => hashset!["href", "title"],
            "img" => hashset!["src", "alt", "title"],
        ]);
        
        cleaner.link_rel(Some(Cow::Borrowed("noopener noreferrer")));
        cleaner.url_relative(UrlRelative::Deny);
        
        Self { cleaner }
    }
    
    pub fn clean(&self, html: &str) -> String {
        self.cleaner.clean(html).to_string()
    }
}

#[derive(Serialize)]
pub struct SafeHtml {
    content: String,
}

impl SafeHtml {
    pub fn new(html: &str, sanitizer: &HtmlSanitizer) -> Self {
        SafeHtml {
            content: sanitizer.clean(html),
        }
    }
}