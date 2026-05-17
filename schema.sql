CREATE SCHEMA IF NOT EXISTS "Assessment_1";
SET search_path TO "Assessment_1";

---Tables

CREATE TABLE event (
    ecode CHAR(4) PRIMARY KEY,
    edesc VARCHAR(20) NOT NULL,
    elocation VARCHAR(20),
    edate DATE NOT NULL,
    etime TIME NOT NULL,
    emax SMALLINT
    CONSTRAINT chk_future_event_date
        CHECK (edate >= CURRENT_DATE)

);

CREATE TABLE spectator (
    sno INTEGER PRIMARY KEY,
    sname VARCHAR(20) NOT NULL,
    semail VARCHAR(20) NOT NULL
);

CREATE TABLE ticket (
    tno INTEGER PRIMARY KEY,
    ecode CHAR(4) NOT NULL,
    sno INTEGER NOT NULL,
    CONSTRAINT fk_ticket_event FOREIGN KEY (ecode)
        REFERENCES event(ecode)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_ticket_spectator FOREIGN KEY (sno)
        REFERENCES spectator(sno)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT ticket_unique UNIQUE (ecode, sno)
);

CREATE TABLE cancel (
    tno INTEGER PRIMARY KEY,
    ecode CHAR(4) NOT NULL,
    sno INTEGER NOT NULL,
    cdate TIMESTAMP,
    cuser VARCHAR(128)
);

---Comments

COMMENT ON TABLE event IS 'Stores information about each event.';
COMMENT ON COLUMN event.ecode IS 'Unique event code (4 characters).';
COMMENT ON COLUMN event.emax IS 'Maximum number of spectators allowed.';

COMMENT ON TABLE spectator IS 'Stores information about spectators.';
COMMENT ON COLUMN spectator.semail IS 'Unique email address for each spectator.';

COMMENT ON TABLE ticket IS 'Links spectators to the events they attend.';
COMMENT ON COLUMN ticket.tno IS 'Unique ticket number.';

COMMENT ON TABLE cancel IS 'Records ticket cancellations with date and user.';

---Views

CREATE VIEW v_event_bookings AS
SELECT
    e.ecode,
    e.edesc,
    COUNT(t.tno) AS total_booked,
    e.emax AS max_capacity,
    (e.emax - COUNT(t.tno)) AS remaining_seats
FROM event e
LEFT JOIN ticket t ON e.ecode = t.ecode
WHERE t.tno NOT IN (SELECT tno FROM cancel)
GROUP BY e.ecode, e.edesc, e.emax;

COMMENT ON VIEW v_event_bookings IS 'Displays number of tickets booked per event, excluding cancellations.';

---Functions

CREATE OR REPLACE FUNCTION fn_ticket_count(p_ecode CHAR(4))
RETURNS INTEGER AS $$
    SELECT COUNT(*) FROM ticket
    WHERE ecode = p_ecode
      AND tno NOT IN (SELECT tno FROM cancel);
$$ LANGUAGE SQL;

COMMENT ON FUNCTION fn_ticket_count(CHAR) IS 'Returns the number of valid (non-cancelled) tickets for an event.';

---Triggers

-- Trigger: prevent overbooking
CREATE OR REPLACE FUNCTION trg_check_capacity()
RETURNS TRIGGER AS $$
DECLARE
    booked INTEGER;
BEGIN
    SELECT COUNT(*) INTO booked
    FROM ticket
    WHERE ecode = NEW.ecode
      AND tno NOT IN (SELECT tno FROM cancel);

    IF booked >= (SELECT emax FROM event WHERE ecode = NEW.ecode) THEN
        RAISE EXCEPTION 'Event % is already full.', NEW.ecode;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_capacity_before_insert
BEFORE INSERT ON ticket
FOR EACH ROW
EXECUTE FUNCTION trg_check_capacity();

COMMENT ON TRIGGER check_capacity_before_insert ON ticket IS 'Prevents inserting tickets when event capacity is reached.';

-- Trigger: move deleted ticket to cancel table
CREATE OR REPLACE FUNCTION trg_move_ticket_to_cancel()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO cancel (tno, ecode, sno, cdate, cuser)
    VALUES (OLD.tno, OLD.ecode, OLD.sno, CURRENT_TIMESTAMP, 'system_user');
    
    RETURN OLD; -- Allow the delete to proceed
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_ticket_delete
BEFORE DELETE ON ticket
FOR EACH ROW
EXECUTE FUNCTION trg_move_ticket_to_cancel();

---Test Data

INSERT INTO event (ecode, edesc, elocation, edate, etime, emax) VALUES
('A100', '100m Sprint', 'Stadium 1', '2026-07-01', '14:00', 5),
('A200', 'Long Jump', 'Stadium 2', '2026-07-02', '10:00', 3),
('A300', 'Swimming Finals', 'Aquatic Ctr', '2026-07-03', '09:30', 2),
('A400', 'High Jump', 'Stadium 3', '2026-07-04', '11:00', 4),
('A500', 'Marathon', 'City Route', '2026-07-05', '09:00', 10);

INSERT INTO spectator (sno, sname, semail) VALUES
(101, 'Alice Brown', 'alice@mail.com'),
(102, 'Bob Smith', 'bob@mail.com'),
(103, 'Carol Jones', 'carol@mail.com'),
(104, 'David Green', 'david@mail.com'),
(105, 'Ella White', 'ella@mail.com'),
(106, 'Frank Black', 'frank@mail.com');

INSERT INTO ticket (tno, ecode, sno) VALUES
(1, 'A100', 101),
(2, 'A100', 102),
(3, 'A200', 101),
(4, 'A200', 103),
(5, 'A300', 104),
(6, 'A400', 105),
(7, 'A500', 106),
(8, 'A500', 101);

INSERT INTO cancel (tno, ecode, sno, cdate, cuser) VALUES
(2, 'A100', 102, '2025-11-27 12:00:00', 'admin'),
(5, 'A300', 104, '2025-11-27 12:05:00', 'admin');