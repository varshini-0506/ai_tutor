import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext.jsx';
import './Calendar.css';

export default function Calendar() {
  const { user } = useAuth();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState([]);
  const [showAddEvent, setShowAddEvent] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [showEventDetails, setShowEventDetails] = useState(false);
  const [newEvent, setNewEvent] = useState({
    title: '',
    description: '',
    date: '',
    time: '',
    type: 'study',
    priority: 'medium'
  });

  // Load events from localStorage
  useEffect(() => {
    if (user?.username) {
      const savedEvents = localStorage.getItem(`calendar_events_${user.username}`);
      if (savedEvents) {
        setEvents(JSON.parse(savedEvents));
      }
    }
  }, [user?.username]);

  // Save events to localStorage
  useEffect(() => {
    if (user?.username) {
      localStorage.setItem(`calendar_events_${user.username}`, JSON.stringify(events));
    }
  }, [events, user?.username]);

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDay = firstDay.getDay();
    
    const days = [];
    
    // Add empty days for padding
    for (let i = 0; i < startingDay; i++) {
      days.push(null);
    }
    
    // Add days of the month
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(new Date(year, month, i));
    }
    
    return days;
  };

  const getEventsForDate = (date) => {
    if (!date) return [];
    return events.filter(event => {
      const eventDate = new Date(event.date);
      return eventDate.toDateString() === date.toDateString();
    });
  };

  const handleAddEvent = (e) => {
    e.preventDefault();
    if (!newEvent.title || !newEvent.date) return;
    
    const event = {
      id: Date.now(),
      ...newEvent,
      createdAt: new Date().toISOString()
    };
    
    setEvents(prev => [...prev, event]);
    setNewEvent({
      title: '',
      description: '',
      date: '',
      time: '',
      type: 'study',
      priority: 'medium'
    });
    setShowAddEvent(false);
  };

  const handleDeleteEvent = (eventId) => {
    setEvents(prev => prev.filter(event => event.id !== eventId));
    setShowEventDetails(false);
  };

  const handleEditEvent = (event) => {
    setSelectedEvent(event);
    setNewEvent({
      title: event.title,
      description: event.description,
      date: event.date,
      time: event.time,
      type: event.type,
      priority: event.priority
    });
    setShowAddEvent(true);
    setShowEventDetails(false);
  };

  const handleUpdateEvent = (e) => {
    e.preventDefault();
    if (!newEvent.title || !newEvent.date) return;
    
    setEvents(prev => prev.map(event => 
      event.id === selectedEvent.id 
        ? { ...event, ...newEvent, updatedAt: new Date().toISOString() }
        : event
    ));
    
    setNewEvent({
      title: '',
      description: '',
      date: '',
      time: '',
      type: 'study',
      priority: 'medium'
    });
    setSelectedEvent(null);
    setShowAddEvent(false);
  };

  const navigateMonth = (direction) => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      newDate.setMonth(prev.getMonth() + direction);
      return newDate;
    });
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'study': return '📚';
      case 'exam': return '📝';
      case 'assignment': return '📋';
      case 'meeting': return '👥';
      case 'break': return '☕';
      default: return '📅';
    }
  };

  const renderCalendar = () => {
    const days = getDaysInMonth(currentDate);
    const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    
    return (
      <div className="calendar-grid">
        <div className="calendar-weekdays">
          {weekdays.map(day => (
            <div key={day} className="weekday">{day}</div>
          ))}
        </div>
        <div className="calendar-days">
          {days.map((day, index) => {
            const dayEvents = getEventsForDate(day);
            const isToday = day && day.toDateString() === new Date().toDateString();
            const isCurrentMonth = day && day.getMonth() === currentDate.getMonth();
            
            return (
              <div 
                key={index} 
                className={`calendar-day ${!day ? 'empty' : ''} ${isToday ? 'today' : ''} ${!isCurrentMonth ? 'other-month' : ''}`}
                onClick={() => day && setShowAddEvent(true)}
              >
                {day && (
                  <>
                    <span className="day-number">{day.getDate()}</span>
                    <div className="event-indicators">
                      {dayEvents.slice(0, 3).map(event => (
                        <div 
                          key={event.id}
                          className="event-indicator"
                          style={{ backgroundColor: getPriorityColor(event.priority) }}
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedEvent(event);
                            setShowEventDetails(true);
                          }}
                          title={event.title}
                        >
                          {getTypeIcon(event.type)}
                        </div>
                      ))}
                      {dayEvents.length > 3 && (
                        <div className="more-events">+{dayEvents.length - 3}</div>
                      )}
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const upcomingEvents = events
    .filter(event => new Date(event.date) >= new Date())
    .sort((a, b) => new Date(a.date) - new Date(b.date))
    .slice(0, 5);

  return (
    <div className="calendar-container">
      <div className="calendar-header">
        <button onClick={() => navigateMonth(-1)} className="nav-btn">‹</button>
        <h2>{currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}</h2>
        <button onClick={() => navigateMonth(1)} className="nav-btn">›</button>
      </div>

      <div className="calendar-main">
        <div className="calendar-section">
          {renderCalendar()}
        </div>

        <div className="upcoming-events">
          <h3>📅 Upcoming Events</h3>
          {upcomingEvents.length === 0 ? (
            <p className="no-events">No upcoming events</p>
          ) : (
            <div className="events-list">
              {upcomingEvents.map(event => (
                <div 
                  key={event.id} 
                  className="event-item"
                  onClick={() => {
                    setSelectedEvent(event);
                    setShowEventDetails(true);
                  }}
                >
                  <div className="event-icon">{getTypeIcon(event.type)}</div>
                  <div className="event-info">
                    <div className="event-title">{event.title}</div>
                    <div className="event-date">
                      {new Date(event.date).toLocaleDateString()}
                      {event.time && ` at ${event.time}`}
                    </div>
                  </div>
                  <div 
                    className="event-priority"
                    style={{ backgroundColor: getPriorityColor(event.priority) }}
                  ></div>
                </div>
              ))}
            </div>
          )}
          <button 
            onClick={() => setShowAddEvent(true)}
            className="add-event-btn"
          >
            ➕ Add Event
          </button>
        </div>
      </div>

      {/* Add/Edit Event Modal */}
      {showAddEvent && (
        <div className="modal-overlay" onClick={() => setShowAddEvent(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedEvent ? 'Edit Event' : 'Add New Event'}</h3>
              <button 
                className="close-button"
                onClick={() => {
                  setShowAddEvent(false);
                  setSelectedEvent(null);
                  setNewEvent({
                    title: '',
                    description: '',
                    date: '',
                    time: '',
                    type: 'study',
                    priority: 'medium'
                  });
                }}
              >
                ×
              </button>
            </div>
            <form onSubmit={selectedEvent ? handleUpdateEvent : handleAddEvent}>
              <div className="form-group">
                <label>Title *</label>
                <input
                  type="text"
                  value={newEvent.title}
                  onChange={e => setNewEvent(prev => ({ ...prev, title: e.target.value }))}
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={newEvent.description}
                  onChange={e => setNewEvent(prev => ({ ...prev, description: e.target.value }))}
                  rows="3"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Date *</label>
                  <input
                    type="date"
                    value={newEvent.date}
                    onChange={e => setNewEvent(prev => ({ ...prev, date: e.target.value }))}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Time</label>
                  <input
                    type="time"
                    value={newEvent.time}
                    onChange={e => setNewEvent(prev => ({ ...prev, time: e.target.value }))}
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Type</label>
                  <select
                    value={newEvent.type}
                    onChange={e => setNewEvent(prev => ({ ...prev, type: e.target.value }))}
                  >
                    <option value="study">📚 Study</option>
                    <option value="exam">📝 Exam</option>
                    <option value="assignment">📋 Assignment</option>
                    <option value="meeting">👥 Meeting</option>
                    <option value="break">☕ Break</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Priority</label>
                  <select
                    value={newEvent.priority}
                    onChange={e => setNewEvent(prev => ({ ...prev, priority: e.target.value }))}
                  >
                    <option value="low">🟢 Low</option>
                    <option value="medium">🟡 Medium</option>
                    <option value="high">🔴 High</option>
                  </select>
                </div>
              </div>
              <div className="modal-actions">
                <button type="submit" className="btn-primary">
                  {selectedEvent ? 'Update Event' : 'Add Event'}
                </button>
                <button 
                  type="button" 
                  className="btn-secondary"
                  onClick={() => {
                    setShowAddEvent(false);
                    setSelectedEvent(null);
                    setNewEvent({
                      title: '',
                      description: '',
                      date: '',
                      time: '',
                      type: 'study',
                      priority: 'medium'
                    });
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Event Details Modal */}
      {showEventDetails && selectedEvent && (
        <div className="modal-overlay" onClick={() => setShowEventDetails(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Event Details</h3>
              <button 
                className="close-button"
                onClick={() => setShowEventDetails(false)}
              >
                ×
              </button>
            </div>
            <div className="event-details">
              <div className="event-header">
                <div className="event-icon-large">{getTypeIcon(selectedEvent.type)}</div>
                <div className="event-title-large">{selectedEvent.title}</div>
                <div 
                  className="event-priority-badge"
                  style={{ backgroundColor: getPriorityColor(selectedEvent.priority) }}
                >
                  {selectedEvent.priority}
                </div>
              </div>
              {selectedEvent.description && (
                <div className="event-description">
                  <h4>Description:</h4>
                  <p>{selectedEvent.description}</p>
                </div>
              )}
              <div className="event-meta">
                <div className="event-date-time">
                  <strong>Date:</strong> {new Date(selectedEvent.date).toLocaleDateString()}
                  {selectedEvent.time && (
                    <span><strong>Time:</strong> {selectedEvent.time}</span>
                  )}
                </div>
                <div className="event-type">
                  <strong>Type:</strong> {selectedEvent.type.charAt(0).toUpperCase() + selectedEvent.type.slice(1)}
                </div>
              </div>
              <div className="event-actions">
                <button 
                  onClick={() => handleEditEvent(selectedEvent)}
                  className="btn-primary"
                >
                  ✏️ Edit
                </button>
                <button 
                  onClick={() => handleDeleteEvent(selectedEvent.id)}
                  className="btn-danger"
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 