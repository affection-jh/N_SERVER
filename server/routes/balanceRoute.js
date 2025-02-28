const express = require("express");
const db = require("../db/db");
const router = express.Router();

 
  router.post("/:userId/update", (req, res) => {
    const user_id = req.params.userId;
    const { balance } = req.body;
  
    db.query(
      "INSERT INTO balances (user_id, balance) VALUES (?, ?) ON DUPLICATE KEY UPDATE balance = VALUES(balance)",
      [user_id, balance],
      (err, result) => {
        if (err) {
          console.error("❌ 잔고 데이터 추가 실패:", err);
          res.status(500).json({ error: "잔고 데이터 추가 실패" });
        } else {
          res.json({ message: "잔고 업데이트 성공", id: result.insertId });
        }
      }
    );
  });
  


router.get("/:userId/fetch", (req, res) => {
    const userId = req.params.userId;
    db.query(
      "SELECT balance AS balance FROM balances WHERE user_id = ?",
      [userId],
      (err, results) => {
        if (err) {
          console.error("❌ 잔고 총액 조회 실패:", err);
          res.status(500).json({ error: "잔고 총액 조회 실패" });
        } else {
          const balance = results[0]?.balance || 0.0;
          res.json({ balance })
        }
      }
    );
  });
  

module.exports = router;