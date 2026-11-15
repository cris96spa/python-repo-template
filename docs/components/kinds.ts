// The kinds of documentation page. The `group` of a pages.json entry names one, and its key
// selects the tint the navigation, the eyebrow above the title and the cards draw it with.
export interface Kind {
  key: string;
  group: string;
  label: string;
}

export const kinds: Kind[] = [
  { key: "overview", group: "Overview", label: "Overview" },
  { key: "tutorial", group: "Tutorial", label: "Tutorial" },
  { key: "howto", group: "How-to guides", label: "How-to guide" },
  { key: "reference", group: "Reference", label: "Reference" },
  { key: "explanation", group: "Explanation", label: "Explanation" },
  { key: "project", group: "Project", label: "Project" },
];

// A group the table does not name keeps its own name and the neutral tint.
export function kindOfGroup(group: string): Kind {
  return kinds.find((kind) => kind.group === group) ?? { key: "project", group, label: group };
}

// A component's `kind` prop accepts a key ("howto") or a group name ("How-to guides").
export function kindNamed(name: string): Kind {
  const wanted = name.toLowerCase();
  const kind = kinds.find((entry) => entry.key === wanted || entry.group.toLowerCase() === wanted);
  if (!kind) {
    const keys = kinds.map((entry) => entry.key).join(", ");
    throw new Error(`Unknown kind "${name}": use one of ${keys}.`);
  }
  return kind;
}
