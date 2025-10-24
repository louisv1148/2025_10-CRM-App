<script lang="ts">
  import { todos } from "../lib/stores";
  import { createTodo, updateTodo, fetchTodos } from "../lib/api";

  let newTodoText = "";

  async function addTodo() {
    if (newTodoText.trim()) {
      await createTodo({
        note_id: 1, // TODO: Use current note ID
        description: newTodoText.trim(),
        status: "pending",
      });
      $todos = await fetchTodos();
      newTodoText = "";
    }
  }

  async function toggleTodo(todo: any) {
    const newStatus = todo.status === "completed" ? "pending" : "completed";
    await updateTodo(todo.id, { status: newStatus });
    $todos = await fetchTodos();
  }
</script>

<section class="todo-list">
  <h3>Action Items</h3>

  <div class="add-todo">
    <input
      type="text"
      placeholder="Add todo..."
      bind:value={newTodoText}
      on:keypress={(e) => e.key === "Enter" && addTodo()}
    />
    <button on:click={addTodo}>+</button>
  </div>

  <div class="todos">
    {#if $todos.length === 0}
      <p class="empty">No action items yet</p>
    {:else}
      {#each $todos as todo}
        <div class="todo-item" class:completed={todo.status === "completed"}>
          <input
            type="checkbox"
            checked={todo.status === "completed"}
            on:change={() => toggleTodo(todo)}
          />
          <span class="todo-text">{todo.description}</span>
        </div>
      {/each}
    {/if}
  </div>
</section>

<style>
  .todo-list {
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  h3 {
    margin-top: 0;
    color: #2c3e50;
    border-bottom: 2px solid #f39c12;
    padding-bottom: 0.5rem;
  }

  .add-todo {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .add-todo input {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.9rem;
  }

  .add-todo button {
    background: #f39c12;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1.2rem;
    font-weight: bold;
  }

  .add-todo button:hover {
    background: #e67e22;
  }

  .todos {
    flex: 1;
    overflow-y: auto;
  }

  .empty {
    color: #999;
    font-size: 0.9rem;
    font-style: italic;
    text-align: center;
    margin-top: 2rem;
  }

  .todo-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem;
    border: 1px solid #eee;
    border-radius: 4px;
    margin-bottom: 0.5rem;
    transition: background 0.2s;
  }

  .todo-item:hover {
    background: #f9f9f9;
  }

  .todo-item.completed {
    opacity: 0.6;
  }

  .todo-item.completed .todo-text {
    text-decoration: line-through;
  }

  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }

  .todo-text {
    flex: 1;
    font-size: 0.9rem;
  }
</style>
