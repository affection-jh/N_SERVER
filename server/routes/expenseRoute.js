const express = require("express");
const db = require("../db/db");
const router = express.Router();

//특정 사용자의 지출 목록 조회
router.get("/:userId", (req, res) => {
    const userId = req.params.userId;
    db.query(
      "SELECT * FROM expenses WHERE user_id = ?",
      [userId],
      (err, results) => {
        if (err) {
          console.error("❌ 데이터 조회 실패:", err);
          res.status(500).json({ error: "데이터 조회 실패" });
        } else {
          if (results.length === 0) {
            res.status(404).json({ message: "데이터가 없습니다" });
          } else {
            res.json(results);
          }
        }
      }
    );
});


//대출 총액 반환
router.get("/:userId/loan-total", (req, res) => {
  const userId = req.params.userId; 
 
  db.query(
    "SELECT COALESCE(SUM(expense), 0) AS total_loan FROM expenses WHERE user_id = ? AND type LIKE '%대출%'",
    [userId],
    (err, results) => {
      if (err) {
        console.error("❌ 대출 총액 조회 실패:", err);
        res.status(500).json({ error: "대출 총액 조회 실패" });
      } else {
        const total_loan = results[0].total_loan ? results[0].total_loan : 0.0;
        res.json({ total_loan })
      }
    }
  );
});

  
  //새 지출 추가
  router.post("/", (req, res) => {
    const {user_id, type, expense, monthly_expense, due_date, interest, code , is_paid } = req.body;
  
    db.query(
      "INSERT INTO expenses (user_id, type, expense, monthly_expense, due_date, interest, code , is_paid) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
      [user_id, type, expense, monthly_expense, due_date, interest, code , is_paid],
      (err, result) => {
        if (err) {
          console.error("❌ 데이터 추가 실패:", err);
          res.status(500).json({ error: "데이터 추가 실패" });
        } else {
          res.json({ message: "지출 추가 성공", id: result.insertId });
        }
      }
    );
  });
  
  //특정 지출 정보 업데이트
  router.post("/:userId/update", (req, res) => {
  const { expense ,due_date ,type, code } = req.body;
  const userId = req.params.userId;
  
    db.query(
    "UPDATE expenses SET expense = ?, due_date = ? WHERE user_id = ? AND type = ? AND code = ?",
      [expense, due_date ,userId, type, code],
      (err, result) => {
        if (err) {
          console.error("❌ 데이터 업데이트 실패:", err);
          res.status(500).json({ error: "데이터 업데이트 실패" });
        }else {
          if (result.affectedRows === 0) {
            // 업데이트된 행이 없으면 에러 처리
            res.status(404).json({ error: "업데이트할 데이터 없음" });
          } 
          else {
            res.json({ message: "지출 업데이트 성공" });
          }}
        }
    );
  });
  
  //특정 지출 삭제
  router.delete("/:userId/:type/:code", (req, res) => {
    const userId = req.params.userId;
    const type = req.params.type;
    const code = req.params.code;
  
    db.query("DELETE FROM expenses WHERE user_id = ? AND type = ? AND code = ?", [userId, type, code], (err, result) => {
      if (err) {
        console.error("❌ 지출 데이터 삭제 실패:", err);
      res.status(500).json({ error: "지출 데이터 삭제 실패" });
      } else {
        res.json({ message: "지출 데이터 삭제 성공" });
      }
    });
  });
  

module.exports = router;