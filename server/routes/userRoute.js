const express = require("express");
const db = require("../db/db");
const router = express.Router();

// 특정 사용자 정보 조회 (GET /users/:userId)
router.get("/:userId/fetch", (req, res) => {
  const userId = req.params.userId;

  db.query(
    "SELECT * FROM users WHERE user_id = ?",
    [userId],
    (err, results) => {
      if (err) {
        console.error("❌ 유저 데이터 조회 실패:", err);
        return res.status(500).json({ error: "데이터 조회 실패" });
      }

      if (results.length === 0) {
        return res.status(404).json({ message: "데이터가 없습니다" });
      }

      res.json(results[0]); 
    }
  );
});

// 사용자 정보 업데이트 (PATCH /users/:userId)
router.patch("/update", (req, res) => {
  const {userId ,attendances, hearts, credit_score ,coins, late_checked_date} = req.body;

  if (attendances === undefined && hearts === undefined && coins === undefined && credit_score === undefined && late_checked_date === undefined) {
    return res.status(400).json({ error: "업데이트할 값이 없습니다." });
  }

  // 동적으로 UPDATE 문 생성 (필요한 필드만 업데이트)
  let updateFields = [];
  let values = [];


  if (attendances !== undefined && attendances !== null) {
    let formattedAttendances = JSON.stringify(attendances).replace(/\\/g, ""); // 백슬래시 제거
    updateFields.push("attendances = ?");
    values.push(formattedAttendances);
  }
  
  if (hearts !== undefined && hearts !== null) {
    updateFields.push("hearts = ?");
    values.push(hearts);
  }
  if (credit_score !== undefined && credit_score !== null) {
    updateFields.push("credit_score = ?");
    values.push(credit_score);
  }
  if (coins !== undefined && coins !== null) {
    updateFields.push("coins = ?");
    values.push(coins);
  }

  if (late_checked_date !== undefined && late_checked_date !== null) {
    updateFields.push("late_checked_date = ?");
    values.push(late_checked_date);
  }


  values.push(userId); // 마지막으로 userId 추가
  const updateQuery = `UPDATE users SET ${updateFields.join(", ")} WHERE user_id = ?`;

  db.query(updateQuery, values, (err, result) => {
    if (err) {
      console.error("❌ 데이터 업데이트 실패:", err);
      return res.status(500).json({ error: "데이터 업데이트 실패" });
    }

    if (result.affectedRows === 0) {
      return res.status(404).json({ error: "업데이트할 데이터 없음" });
    }

    res.json({ message: "✅ 사용자 정보 업데이트 성공" });
  });
});

// 신규 사용자 정보 등록
router.post("/enroll", (req, res) => {
  const { userId, attendances, hearts, credit_score , coins, late_checked_date} = req.body;
  const attendanceJson = JSON.stringify(attendances);

  if (!userId || !attendances) {
    return res.status(400).json({ error: "userId와 attendances가 필요합니다." });
  }


  db.query(
    "INSERT INTO users (user_id, attendances, hearts, coins, credit_score, late_checked_date) VALUES (?, ?, ?, ?, ?, ?)",
    [userId, attendanceJson, hearts || 7, coins || 0, credit_score || 750, late_checked_date || "2005-08-30"],
    (err, result) => {
      if (err) {
        console.error("❌ 데이터 등록 실패:", err);
        return res.status(500).json({ error: "데이터 등록 실패" });
      }
      res.status(201).json({ message: "✅ 신규 사용자 데이터 등록 성공" });
    }
  );
});
module.exports = router;
