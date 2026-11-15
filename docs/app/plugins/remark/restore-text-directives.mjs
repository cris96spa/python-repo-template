// Turn text (`:name`) and leaf (`::name`) directives back into the text they were written as.
// The engine defines only the `:::output` container, while remark-directive 4 reads any colon
// followed by a word or a number as a directive, such as the port in http://127.0.0.1:8031/.
// Requires remark-directive to be applied before this plugin

export default function remarkRestoreTextDirectives() {
  return (tree, file) => {
    const source = String(file.value ?? '');
    const restore = (node) => {
      const start = node.position?.start?.offset;
      const end = node.position?.end?.offset;
      if (start == null || end == null) return null;
      const text = { type: 'text', value: source.slice(start, end) };
      return node.type === 'leafDirective' ? { type: 'paragraph', children: [text] } : text;
    };

    const visit = (node) => {
      if (!node || !Array.isArray(node.children)) return;
      node.children = node.children.map((child) => {
        if (child.type === 'textDirective' || child.type === 'leafDirective') {
          return restore(child) ?? child;
        }
        visit(child);
        return child;
      });
    };

    visit(tree);
  };
}
