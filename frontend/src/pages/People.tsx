import { useEffect, useState } from "react";
import {
  createPerson,
  deactivatePerson,
  fetchPersons,
  Person,
  PersonType,
  trainPerson,
  updatePerson,
} from "../api/persons";

const emptyForm = {
  name: "",
  email: "",
  department: "",
  person_code: "",
  person_type: "student" as PersonType,
};

const People = () => {
  const [people, setPeople] = useState<Person[]>([]);
  const [filter, setFilter] = useState<PersonType | "all">("all");
  const [form, setForm] = useState(emptyForm);
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);

  const load = async () => {
    const data = await fetchPersons(filter === "all" ? undefined : filter);
    setPeople(data.persons);
  };

  useEffect(() => {
    load();
  }, [filter]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      if (editingId) {
        await updatePerson(editingId, {
          name: form.name,
          email: form.email || null,
          department: form.department || null,
          person_code: form.person_code || null,
          person_type: form.person_type,
        });
        if (files.length) {
          await trainPerson({
            person_id: editingId,
            name: form.name,
            person_type: form.person_type,
            email: form.email || undefined,
            department: form.department || undefined,
            person_code: form.person_code || undefined,
            files,
          });
          setMessage("Person updated and retrained successfully.");
        } else {
          setMessage("Person updated successfully.");
        }
      } else {
        const created = await createPerson({
          name: form.name,
          email: form.email || null,
          department: form.department || null,
          person_code: form.person_code || null,
          person_type: form.person_type,
        });
        if (files.length) {
          await trainPerson({
            person_id: created.id,
            name: form.name,
            person_type: form.person_type,
            email: form.email || undefined,
            department: form.department || undefined,
            person_code: form.person_code || undefined,
            files,
          });
        }
        setMessage("Person created and trained successfully.");
      }
      setForm(emptyForm);
      setFiles([]);
      setEditingId(null);
      await load();
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || "Failed to save person");
    } finally {
      setLoading(false);
    }
  };

  const startEdit = (person: Person) => {
    setEditingId(person.id);
    setForm({
      name: person.name || "",
      email: person.email || "",
      department: person.department || "",
      person_code: person.person_code || "",
      person_type: person.person_type,
    });
    setFiles([]);
    setMessage(null);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setForm(emptyForm);
    setFiles([]);
    setMessage(null);
  };

  const handleDelete = async (person: Person) => {
    const confirmed = window.confirm(`Delete ${person.name}? This will remove all data.`);
    if (!confirmed) return;
    setLoading(true);
    setMessage(null);
    try {
      await deactivatePerson(person.id);
      setMessage("Person deleted.");
      await load();
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || "Failed to delete person");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="stack">
      <div className="card">
        <div className="row-between">
          <h3>Students & Staff</h3>
          <div className="row">
            <label className="muted">Filter</label>
            <select value={filter} onChange={(e) => setFilter(e.target.value as any)}>
              <option value="all">All</option>
              <option value="student">Students</option>
              <option value="staff">Staff</option>
            </select>
          </div>
        </div>
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Code</th>
              <th>Department</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {people.map((person) => (
              <tr key={person.id}>
                <td>{person.name}</td>
                <td className="badge">{person.person_type}</td>
                <td>{person.person_code || "-"}</td>
                <td>{person.department || "-"}</td>
                <td className="row">
                  <button className="ghost-button" onClick={() => startEdit(person)}>
                    Edit
                  </button>
                  <button className="danger" onClick={() => handleDelete(person)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
            {!people.length && (
              <tr>
                <td colSpan={5} className="muted">
                  No people found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <form className="card form" onSubmit={handleSubmit}>
        <h4>{editingId ? "Edit Person" : "Add Person + Train Face"}</h4>
        <div className="grid-2">
          <label>
            Full Name
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
          </label>
          <label>
            Person Type
            <select
              value={form.person_type}
              onChange={(e) =>
                setForm({ ...form, person_type: e.target.value as PersonType })
              }
            >
              <option value="student">Student</option>
              <option value="staff">Staff</option>
            </select>
          </label>
          <label>
            Email
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </label>
          <label>
            Department
            <input
              value={form.department}
              onChange={(e) => setForm({ ...form, department: e.target.value })}
            />
          </label>
          <label>
            Student/Employee ID
            <input
              value={form.person_code}
              onChange={(e) => setForm({ ...form, person_code: e.target.value })}
            />
          </label>
          <label>
            Face Images (2-5)
            <input
              type="file"
              multiple
              accept="image/*"
              onChange={(e) => setFiles(Array.from(e.target.files || []))}
            />
            <div className="muted">
              Use clear photos with different angles/lighting for best accuracy.
            </div>
          </label>
        </div>
        {message && <div className="muted">{message}</div>}
        <div className="row">
          <button className="primary" type="submit" disabled={loading}>
            {loading ? "Saving..." : editingId ? "Save Changes" : "Create & Train"}
          </button>
          {editingId && (
            <button className="ghost-button" type="button" onClick={cancelEdit}>
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default People;
