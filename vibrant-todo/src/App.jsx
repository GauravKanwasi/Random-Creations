import { useState, useEffect } from 'react';
import './index.css';

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [newTask, setNewTask] = useState('');
  const [totalPoints, setTotalPoints] = useState(0);
  const [showCelebration, setShowCelebration] = useState(false);

  // Load tasks from localStorage
  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem('tasks')) || [];
    setTasks(saved);
    updatePoints(saved);
  }, []);

  const updatePoints = (tasks) => {
    const points = tasks.reduce((acc, task) => acc + (task.completed ? task.points : 0), 0);
    setTotalPoints(points);
    if (points % 100 === 0 && points > 0) {
      setShowCelebration(true);
      setTimeout(() => setShowCelebration(false), 2000);
    }
  };

  const addTask = () => {
    if (newTask.trim()) {
      const newTasks = [...tasks, {
        text: newTask,
        completed: false,
        points: Math.floor(Math.random() * 50) + 10
      }];
      setTasks(newTasks);
      localStorage.setItem('tasks', JSON.stringify(newTasks));
      setNewTask('');
    }
  };

  const deleteTask = (index) => {
    const newTasks = tasks.filter((_, i) => i !== index);
    setTasks(newTasks);
    localStorage.setItem('tasks', JSON.stringify(newTasks));
    updatePoints(newTasks);
  };

  const toggleComplete = (index) => {
    const newTasks = tasks.map((task, i) => 
      i === index ? { ...task, completed: !task.completed } : task
    );
    setTasks(newTasks);
    localStorage.setItem('tasks', JSON.stringify(newTasks));
    updatePoints(newTasks);
  };

  return (
    <div className="container">
      <h1>🎮 Gamified To-Do (Points: {totalPoints})</h1>
      
      {showCelebration && (
        <div className="confetti-message">
          🎉 Level Up! +100 Points!
        </div>
      )}

      <div>
        <input 
          className="task-input"
          value={newTask} 
          onChange={(e) => setNewTask(e.target.value)} 
          placeholder="Add a quest..."
        />
        <button className="add-button" onClick={addTask}>
          Add Task 🚀
        </button>
      </div>

      {tasks.map((task, index) => (
        <div key={index} className="task-item">
          <span style={{ textDecoration: task.completed ? 'line-through' : 'none' }}>
            {task.text} 🎯 {task.points}
          </span>
          <div>
            <button 
              className="action-button"
              onClick={() => toggleComplete(index)}
            >
              {task.completed ? 'Undo' : 'Complete'}
            </button>
            <button 
              className="delete-button"
              onClick={() => deleteTask(index)}
            >
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}