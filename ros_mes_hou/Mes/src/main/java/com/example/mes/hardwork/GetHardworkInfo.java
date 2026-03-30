package com.example.mes.hardwork;

import com.example.mes.mapper.Hardworkmapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import pojo.Hardwork;
import pojo.Result;

import java.util.List;

@RestController
@CrossOrigin(origins = "*")
public class GetHardworkInfo {
    @Autowired
    private Hardworkmapper hardworkmapper;

    @GetMapping("/hardwork")
    public Result selectall(){
        List<Hardwork> hardworks= hardworkmapper.selectAll();
        System.out.println(hardworks);
        return Result.success(hardworks);
    }
}
